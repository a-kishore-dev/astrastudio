import streamlit as st
from streamlit import session_state as ss
from my_agent import MyAgent
import db_utils

class PageAgents:
    def __init__(self):
        self.name = "Agents"

    def create_agent(self, crew=None):
        agent = MyAgent()
        if 'agents' not in ss:
            ss.agents = []
        ss.agents.append(agent)
        agent.edit = True
        # Add the user_id here
        db_utils.save_agent(agent, ss.user_id) 

        if crew:
            crew.agents.append(agent)
            db_utils.save_crew(crew, ss.user_id)
        return agent

    def draw(self):
        if 'agents' not in ss:
            ss.agents = db_utils.load_agents(ss.user_id)
        if 'crews' not in ss:
            ss.crews = db_utils.load_crews(ss.user_id)

        editing = any(agent.edit for agent in ss.agents)

        with st.container():
            # ---- Page header ----
            st.markdown(
                """
                <div style="margin-bottom: 20px;">
                    <h1 style="font-size:48px; margin-bottom:6px; color:#58A6FF;">🤖 Agents</h1>
                    <p style="font-size:18px; opacity:0.75;">
                        Define autonomous units that execute tasks and collaborate.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ---- ACTION BAR (Single Create Button) ----
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("➕ Create Agent", type="primary", disabled=editing, use_container_width=True):
                    self.create_agent()
                    st.rerun()

            st.markdown("---")

            if len(ss.agents) == 0:
                st.info("No agents defined yet. Click the button above to create your first agent.")
                return

            # Dictionary to track agent assignment
            agent_assignment = {agent.id: [] for agent in ss.agents}
            for crew in ss.crews:
                for agent in crew.agents:
                    agent_assignment[agent.id].append(crew.name)

            # Display agents grouped by crew in tabs
            tabs = ["All Agents", "Unassigned"] + [crew.name for crew in ss.crews]
            tab_objects = st.tabs(tabs)

            # ---- All Agents Tab ----
            with tab_objects[0]:
                for agent in ss.agents:
                    agent.draw()

            # ---- Unassigned Agents Tab ----
            with tab_objects[1]:
                unassigned_agents = [agent for agent in ss.agents if not agent_assignment.get(agent.id)]
                if not unassigned_agents:
                    st.caption("All agents are currently assigned to crews.")
                for agent in unassigned_agents:
                    agent.draw(key="unassigned")

            # ---- Specific Crew Tabs ----
            for i, crew in enumerate(ss.crews, 2):
                with tab_objects[i]:
                    if not crew.agents:
                        st.caption("No agents assigned to this crew yet.")
                    for agent in crew.agents:
                        agent.draw(key=f"crew_{crew.id}")