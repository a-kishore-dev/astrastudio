import re
import streamlit as st
from crewai import TaskOutput
from streamlit import session_state as ss
import threading
import ctypes
import queue
import time
import traceback
import os
from console_capture import ConsoleCapture
import db_utils
from utils import format_result, generate_printable_view, rnd_id, get_tasks_outputs_str


class PageCrewRun:
    def __init__(self):
        self.name = "Kickoff!"
        self.maintain_session_state()
        # FIX: Pass user_id to load_results
        if 'results' not in ss and 'user_id' in ss:
            ss.results = db_utils.load_results(ss.user_id)

    def get_tasks_output(self, tasks_output: list[TaskOutput], tasks=None):
        res = []
        index = 0
        for task_output in tasks_output:
            task_desc = None
            if tasks and index < len(tasks):
                task_desc = getattr(tasks[index], 'description', None)
            res.append({
                'raw': task_output.raw,
                'type': 'TaskOutput',
                'index': index,
                'description': task_desc
            })
            index += 1
        return res

    @staticmethod
    def maintain_session_state():
        defaults = {
            'crew_thread': None,
            'result': None,
            'running': False,
            'message_queue': queue.Queue(),
            'selected_crew_name': None,
            'placeholders': {},
            'console_output': [],
            'last_update': time.time(),
            'console_expanded': True,
        }
        for key, value in defaults.items():
            if key not in ss:
                ss[key] = value

    @staticmethod
    def extract_placeholders(text):
        return re.findall(r'\{(.*?)\}', text)

    def get_placeholders_from_crew(self, crew):
        placeholders = set()
        attributes = ['description', 'expected_output', 'role', 'backstory', 'goal']
        
        for task in crew.tasks:
            placeholders.update(self.extract_placeholders(task.description))
            placeholders.update(self.extract_placeholders(task.expected_output))
        
        for agent in crew.agents:
            for attr in attributes[2:]:
                placeholders.update(self.extract_placeholders(getattr(agent, attr)))
        
        return placeholders

    def run_crew(self, crewai_crew, inputs, message_queue):
        if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
            import agentops
            agentops.start_session()
        try:
            result = crewai_crew.kickoff(inputs=inputs)
            message_queue.put({"result": result})
        except Exception as e:
            if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
                agentops.end_session()
            stack_trace = traceback.format_exc()
            print(f"Error running crew: {str(e)}\n{stack_trace}")
            message_queue.put({"result": f"Error running crew: {str(e)}", "stack_trace": stack_trace})
        finally:
            if hasattr(ss, 'console_capture'):
                ss.console_capture.stop()

    def get_mycrew_by_name(self, crewname):
        return next((crew for crew in ss.crews if crew.name == crewname), None)

    def draw_placeholders(self, crew):
        placeholders = self.get_placeholders_from_crew(crew)
        if placeholders:
            st.write('Placeholders to fill in:')
            for placeholder in placeholders:
                placeholder_key = f'placeholder_{placeholder}'
                ss.placeholders[placeholder_key] = st.text_area(
                    label=placeholder,
                    key=placeholder_key,
                    value=ss.placeholders.get(placeholder_key, ''),
                    disabled=ss.running
                )

    def draw_crews(self):
        if 'crews' not in ss or not ss.crews:
            st.write("No crews defined yet.")
            ss.selected_crew_name = None 
            return

        if ss.selected_crew_name not in [crew.name for crew in ss.crews]:
            ss.selected_crew_name = None

        selected_crew_name = st.selectbox(
            label="Select crew to run",
            options=[crew.name for crew in ss.crews],
            index=0 if ss.selected_crew_name is None else [crew.name for crew in ss.crews].index(ss.selected_crew_name) if ss.selected_crew_name in [crew.name for crew in ss.crews] else 0,
            disabled=ss.running
        )

        if selected_crew_name != ss.selected_crew_name:
            ss.selected_crew_name = selected_crew_name
            st.rerun()

        selected_crew = self.get_mycrew_by_name(ss.selected_crew_name)

        if selected_crew:
            selected_crew.draw(expanded=False,buttons=False)
            self.draw_placeholders(selected_crew)
            
            if not selected_crew.is_valid(show_warning=True):
                st.error("Selected crew is not valid. Please fix the issues.")
            self.control_buttons(selected_crew)

    def control_buttons(self, selected_crew):
        # Add a small helper column for clearing
        col_run, col_clear = st.columns([4, 1])
        
        with col_clear:
            if st.button("Reset Inputs", help="Clear all placeholder values"):
                ss.placeholders = {}
                st.rerun()

        with col_run:
            if st.button('Run crew!', type="primary", disabled=not selected_crew.is_valid() or ss.running, use_container_width=True):
                # --- NEW ROBUST PLACEHOLDER LOGIC ---
                # 1. Identify exactly what placeholders the current crew needs
                needed = self.get_placeholders_from_crew(selected_crew)
                
                # 2. Build the inputs dict by matching the "placeholder_" key precisely
                inputs = {}
                for p_name in needed:
                    # Look for the key in session state
                    p_key = f'placeholder_{p_name}'
                    if p_key in ss.placeholders:
                        val = ss.placeholders[p_key]
                        # Set the key as exactly what was found in the {brackets}
                        inputs[p_name] = val
                    else:
                        # Fallback if empty
                        inputs[p_name] = ""

                # DEBUG: uncomment the line below if you still have issues to see the dict in console
                # print(f"DEBUG: Running crew with inputs: {inputs}")

                ss.result = None
                try:
                    crew = selected_crew.get_crewai_crew(full_output=True)
                except Exception as e:
                    st.exception(e)
                    return

                ss.console_capture = ConsoleCapture()
                ss.console_capture.start()
                ss.console_output = [] 

                ss.running = True
                ss.crew_thread = threading.Thread(
                    target=self.run_crew,
                    kwargs={
                        "crewai_crew": crew,
                        "inputs": inputs, # This dict now perfectly matches {topic}
                        "message_queue": ss.message_queue
                    }
                )
                ss.crew_thread.start()
                st.rerun()
                
    def serialize_result(self, result, crew=None) -> str | dict :
        if isinstance(result, dict):
            serialized = {}
            for key, value in result.items():
                if hasattr(value, 'raw'):
                    serialized[key] = {
                        'raw': value.raw,
                        'type': 'CrewOutput'
                    }
                    tasks_output_key = 'tasks_output'
                    if hasattr(value, tasks_output_key):
                        serialized[tasks_output_key] = self.get_tasks_output(
                            value.tasks_output,
                            crew.tasks if crew else None
                        )
                elif hasattr(value, '__dict__'):
                    serialized[key] = {
                        'data': value.__dict__,
                        'type': value.__class__.__name__
                    }
                else:
                    serialized[key] = value
            return serialized
        return str(result)

    def display_result(self):
        if ss.running and ss.page != "Kickoff!":
            ss.page = "Kickoff!"
            st.rerun()
        console_container = st.empty()
        
        with console_container.container():
            with st.expander("Console Output", expanded=False):
                col1, col2 = st.columns([6,1])
                with col2:
                    if st.button("Clear console"):
                        ss.console_output = []
                        st.rerun()

                console_text = "\n".join(ss.console_output)
                st.code(console_text, language=None)

        if ss.result is not None:
            if isinstance(ss.result, dict):
                from result import Result
                result_identifier = str(hash(str(ss.result)))
                
                if not hasattr(ss, 'saved_results'):
                    ss.saved_results = set()
                
                if result_identifier not in ss.saved_results:
                    relevant_placeholders = {}
                    curr_crew = self.get_mycrew_by_name(ss.selected_crew_name)
                    if curr_crew:
                        crew_placeholders = self.get_placeholders_from_crew(curr_crew)
                        for placeholder in crew_placeholders:
                            placeholder_key = f'placeholder_{placeholder}'
                            if placeholder_key in ss.placeholders:
                                relevant_placeholders[placeholder_key] = ss.placeholders[placeholder_key]
                    
                    result_obj = Result(
                        id=f"R_{rnd_id()}",
                        crew_id=ss.selected_crew_name,
                        crew_name=ss.selected_crew_name,
                        inputs={key.split('_')[1]: value for key, value in relevant_placeholders.items()},
                        result=self.serialize_result(ss.result, curr_crew)
                    )
                    
                    db_utils.save_result(result_obj, ss.user_id)
                    
                    if 'results' not in ss:
                        ss.results = []
                    ss.results.append(result_obj)
                    ss.saved_results.add(result_identifier)

                formatted_result = format_result(ss.result)
                st.expander("Final output", expanded=True).write(formatted_result)
                st.expander("Full output", expanded=False).write(ss.result)

                curr_crew = self.get_mycrew_by_name(ss.selected_crew_name)
                task_list = curr_crew.tasks if curr_crew else None
                tasks_result = get_tasks_outputs_str(
                    ss.result["result"].tasks_output,
                    task_list
                )
                formatted_tasks_result = format_result(tasks_result)
                st.expander("Tasks results", expanded=False).write(formatted_tasks_result)

                relevant_inputs = {}
                if curr_crew:
                    crew_placeholders = self.get_placeholders_from_crew(curr_crew)
                    for placeholder in crew_placeholders:
                        placeholder_key = f'placeholder_{placeholder}'
                        if placeholder_key in ss.placeholders:
                            relevant_inputs[placeholder] = ss.placeholders[placeholder_key]

                html_content = generate_printable_view(
                    ss.selected_crew_name,
                    ss.result,
                    relevant_inputs,
                    formatted_result
                )
                if st.button("Open Printable View"):
                    js = f"""
                    <script>
                        var printWindow = window.open('', '_blank');
                        printWindow.document.write({html_content!r});
                        printWindow.document.close();
                    </script>
                    """
                    st.components.v1.html(js, height=0)

                html_tasks_content = generate_printable_view(
                    ss.selected_crew_name,
                    ss.result,
                    relevant_inputs,
                    formatted_tasks_result
                )
                if st.button("Open Printable Complete View"):
                    js = f"""
                    <script>
                        var printWindow = window.open('', '_blank');
                        printWindow.document.write({html_tasks_content!r});
                        printWindow.document.close();
                    </script>
                    """
                    st.components.v1.html(js, height=0)
            else:
                st.error(ss.result)
        elif ss.running and ss.crew_thread is not None:
            with st.spinner("Running crew..."):
                if hasattr(ss, 'console_capture'):
                    new_output = ss.console_capture.get_output()
                    if new_output:
                        ss.console_output.extend(new_output)

                try:
                    message = ss.message_queue.get_nowait()
                    ss.result = message
                    ss.running = False
                    if hasattr(ss, 'console_capture'):
                        ss.console_capture.stop()
                    st.rerun()
                except queue.Empty:
                    time.sleep(1)
                    st.rerun()

    @staticmethod
    def force_stop_thread(thread):
        if thread:
            tid = ctypes.c_long(thread.ident)
            if tid:
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
                if res == 0:
                    st.error("Nonexistent thread id")
                else:
                    st.success("Thread stopped successfully.")

    def draw(self):
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h1 style="font-size:48px; margin-bottom:6px; color:#58A6FF;">🚀 Kickoff!</h1>
                <p style="font-size:18px; opacity:0.75;">
                    Kickoff starts the execution of a crew. During execution, agents collaborate
                    to complete tasks using the defined tools, knowledge sources, and inputs.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        self.draw_crews()
        self.display_result()