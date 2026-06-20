import streamlit as st
from utils import rnd_id
from my_tools import TOOL_CLASSES
from streamlit import session_state as ss
import db_utils

class PageTools:
    def __init__(self):
        self.name = "Tools"
        self.available_tools = TOOL_CLASSES

    def create_tool(self, tool_name):
        tool_class = self.available_tools[tool_name]
        tool_instance = tool_class(rnd_id())
        if 'tools' not in ss:
            ss.tools = []
        ss.tools.append(tool_instance)
        db_utils.save_tool(tool_instance, ss.user_id)  # Save tool to database

    def remove_tool(self, tool_id):
        ss.tools = [tool for tool in ss.tools if tool.tool_id != tool_id]
        db_utils.delete_tool(tool_id, ss.user_id)
        st.rerun()

    def set_tool_parameter(self, tool_id, param_name, value):
        if value == "":
            value = None
        for tool in ss.tools:
            if tool.tool_id == tool_id:
                tool.set_parameters(**{param_name: value})
                db_utils.save_tool(tool, ss.user_id)
                break

    def get_tool_display_name(self, tool):
        first_param_name = tool.get_parameter_names()[0] if tool.get_parameter_names() else None
        first_param_value = tool.parameters.get(first_param_name, '') if first_param_name else ''
        return f"{tool.name} ({first_param_value if first_param_value else tool.tool_id})"

    def draw_tools(self):
        # ---- Tool selector ----
        tool_names = list(self.available_tools.keys())

        st.markdown("### Add a tool")

        selected_tool = st.selectbox(
            "Select a tool to enable",
            options=["— Select a tool —"] + tool_names,
            label_visibility="collapsed",
        )

        if selected_tool != "— Select a tool —":
            tool_class = self.available_tools[selected_tool]
            tool_instance = tool_class()
            st.caption(tool_instance.description)

            if st.button(f"➕ Add {selected_tool}", use_container_width=False):
                self.create_tool(selected_tool)
                st.rerun()

        st.markdown("---")

        # ---- Enabled tools ----
        st.markdown("### Enabled tools")

        if 'tools' not in ss or len(ss.tools) == 0:
            st.info("No tools enabled yet.")
            return

        for tool in ss.tools:
            display_name = self.get_tool_display_name(tool)
            is_complete = tool.is_valid()
            expander_title = display_name if is_complete else f"❗ {display_name}"

            with st.expander(expander_title, expanded=not is_complete):
                st.write(tool.description)

                for param_name in tool.get_parameter_names():
                    param_value = tool.parameters.get(param_name, "")
                    placeholder = (
                        "Required"
                        if tool.is_parameter_mandatory(param_name)
                        else "Optional"
                    )

                    new_value = st.text_input(
                        param_name,
                        value=param_value,
                        placeholder=placeholder,
                        key=f"{tool.tool_id}_{param_name}",
                    )

                    if new_value != param_value:
                        self.set_tool_parameter(tool.tool_id, param_name, new_value)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button(
                    "🗑 Remove tool",
                    key=f"remove_{tool.tool_id}",
                ):
                    self.remove_tool(tool.tool_id)


    def draw(self):
        with st.container():

            # ---- Page header (COMMON STYLE) ----
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h1 style="font-size:48px; margin-bottom:6px;">🛠️ Tools</h1>
                    <p style="font-size:18px; opacity:0.75;">
                        Tools empower agents with capabilities such as web searching, data analysis,
                        and collaboration. A tool represents a skill or function that agents can use
                        to perform actions and achieve objectives.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ---- Documentation summary ----
            st.markdown(
                """
                <div style="
                    border-radius: 12px;
                    padding: 14px 16px;
                    border: 1px solid rgba(255,255,255,0.08);
                    background: rgba(255,255,255,0.02);
                    max-width: 500px;
                    margin-bottom: 24px;
                    font-size: 18px;
                ">
                    <strong>What is a Tool?</strong>
                    <p style="margin-top:6px; opacity:0.9;">
                        A tool is a reusable capability that agents can invoke to perform actions.
                        Tools may come from the CrewAI Toolkit, LangChain integrations, or custom
                        implementations, enabling anything from simple searches to complex
                        collaborative workflows.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("---")

            self.draw_tools()

