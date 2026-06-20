import streamlit as st
from streamlit import session_state as ss
from my_task import MyTask
import db_utils

class PageTasks:
    def __init__(self):
        self.name = "Tasks"

    def create_task(self, crew=None):
        # Ensure tasks list exists in session state
        if 'tasks' not in ss:
            ss.tasks = []
            
        # Create a new task instance
        task = MyTask()   
        ss.tasks.append(task)
        task.edit = True # Set to edit mode immediately for user input
        db_utils.save_task(task, ss.user_id)  # Persist to database

        # If created from a specific crew tab, associate it
        if crew:
            crew.tasks.append(task)
            db_utils.save_crew(crew, ss.user_id)

        return task

    def draw(self):
        # Initial data load from DB if session state is empty
        if 'tasks' not in ss:
            ss.tasks = db_utils.load_tasks(ss.user_id)
        if 'crews' not in ss:
            ss.crews = db_utils.load_crews(ss.user_id)
        if 'agents' not in ss:
            ss.agents = db_utils.load_agents(ss.user_id)

        # Check if any task is currently in edit mode to disable the create button
        editing = any(task.edit for task in ss.tasks)

        with st.container():
            # ---- Page Header (Cyber Blue Style) ----
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h1 style="font-size:48px; margin-bottom:6px; color:#58A6FF;">📝 Tasks</h1>
                    <p style="font-size:18px; opacity:0.75;">
                        Define assignments, set expected outputs, and assign agents to your crew's workflow.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ---- ACTION BAR (Single consistent Create Button) ----
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("➕ Create Task", type="primary", disabled=editing, use_container_width=True):
                    self.create_task()
                    st.rerun()

            st.markdown("---")

            # Handle Empty State
            if len(ss.tasks) == 0:
                st.info("No tasks defined yet. Use the 'Create Task' button above to get started.")
                return

            # Dictionary to track which crews a task is assigned to
            task_assignment = {task.id: [] for task in ss.tasks}
            for crew in ss.crews:
                for task in crew.tasks:
                    if task.id in task_assignment:
                        task_assignment[task.id].append(crew.name)

            # Display tasks grouped by crew in tabs
            tabs = ["All Tasks", "Unassigned"] + [crew.name for crew in ss.crews]
            tab_objects = st.tabs(tabs)

            # ---- Tab 0: All Tasks ----
            with tab_objects[0]:
                for task in ss.tasks:
                    task.draw()

            # ---- Tab 1: Unassigned Tasks ----
            with tab_objects[1]:
                unassigned_tasks = [t for t in ss.tasks if not task_assignment.get(t.id)]
                if not unassigned_tasks:
                    st.caption("All tasks are currently assigned to crews.")
                else:
                    for task in unassigned_tasks:
                        task.draw(key="unassigned_tab")

            # ---- Tab 2+: Specific Crew Tabs ----
            for i, crew in enumerate(ss.crews, 2):
                with tab_objects[i]:
                    if not crew.tasks:
                        st.caption(f"No tasks assigned to '{crew.name}' yet.")
                    else:
                        for task in crew.tasks:
                            # Use a unique key based on crew ID to prevent Streamlit widget ID collisions
                            task.draw(key=f"crew_tab_{crew.id}")