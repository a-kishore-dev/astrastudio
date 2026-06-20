import streamlit as st
from streamlit import session_state as ss
from my_crew import MyCrew
from my_agent import MyAgent
from my_task import MyTask
from my_tools import TOOL_CLASSES
import db_utils
from crewai import Process

class PageCrews:
    def __init__(self):
        self.name = "Crews"

    def create_crew(self):
        crew = MyCrew()
        if 'crews' not in ss:
            ss.crews = []
        ss.crews.append(crew)
        crew.edit = True
        db_utils.save_crew(crew, ss.user_id)
        return crew

    def apply_template(self, template_key):
        """Logic to build a complete crew from a template."""
        # Ensure collections exist
        if 'agents' not in ss: ss.agents = db_utils.load_agents(ss.user_id)
        if 'tasks' not in ss: ss.tasks = db_utils.load_tasks(ss.user_id)
        if 'tools' not in ss: ss.tools = db_utils.load_tools(ss.user_id)

        # Helper: Get or Create Tool
        def get_tool(name):
            existing = next((t for t in ss.tools if t.name == name), None)
            if existing: return existing
            # Create new instance of tool if it doesn't exist
            tool_class = TOOL_CLASSES.get(name)
            if tool_class:
                new_tool = tool_class()
                ss.tools.append(new_tool)
                db_utils.save_tool(new_tool, ss.user_id)
                return new_tool
            return None

        # 1. Define Templates
        templates = {
            "web_researcher": {
                "crew_name": "Deep Research Crew",
                "agents": [
                    {"role": "Internet Researcher", "goal": "Extract raw data from the web", "backstory": "Expert at finding hidden info.", "tools": ["DuckDuckGoSearchTool"]},
                    {"role": "Technical Writer", "goal": "Summarize data into reports", "backstory": "Professional editor.", "tools": []}
                ],
                "tasks": [
                    {"desc": "Search for latest news on {topic}", "out": "Bullet points of 10 key facts", "agent_idx": 0},
                    {"desc": "Write a 3-paragraph summary of the findings", "out": "A clean markdown report", "agent_idx": 1}
                ]
            },
            "coder": {
                "crew_name": "Autonomous Developer Crew",
                "agents": [
                    {"role": "Senior Python Developer", "goal": "Write and test python code", "backstory": "10x engineer who uses sandboxed environments.", "tools": ["CodeInterpreterTool"]}
                ],
                "tasks": [
                    {"desc": "Create a script to solve: {problem}", "out": "The logic and the result of the execution", "agent_idx": 0}
                ]
            },
            "mcp_expert": {
                "crew_name": "System Integration Crew",
                "agents": [
                    {"role": "Infrastructure Agent", "goal": "Manage local system resources via MCP", "backstory": "Specialized in using Model Context Protocol.", "mcp_ids": ["local-files"]}
                ],
                "tasks": [
                    {"desc": "Analyze the filesystem context and suggest optimizations", "out": "List of system insights", "agent_idx": 0}
                ]
            }
        }

        # 2. Build the Crew
        data = templates.get(template_key)
        if not data: return

        new_agents = []
        for a_data in data["agents"]:
            agent = MyAgent(
                role=a_data["role"], 
                goal=a_data["goal"], 
                backstory=a_data["backstory"],
                llm_provider_model="Gemini: gemini-1.5-flash" # Defaulting to your preferred Gemini
            )
            # Add Tools
            for t_name in a_data.get("tools", []):
                t_obj = get_tool(t_name)
                if t_obj: agent.tools.append(t_obj)
            # Add MCP IDs
            if "mcp_ids" in a_data:
                agent.mcp_ids = a_data["mcp_ids"]
            
            ss.agents.append(agent)
            db_utils.save_agent(agent, ss.user_id)
            new_agents.append(agent)

        new_tasks = []
        for t_data in data["tasks"]:
            task = MyTask(
                description=t_data["desc"],
                expected_output=t_data["out"],
                agent=new_agents[t_data["agent_idx"]]
            )
            ss.tasks.append(task)
            db_utils.save_task(task, ss.user_id)
            new_tasks.append(task)

        crew = MyCrew(name=data["crew_name"])
        crew.agents = new_agents
        crew.tasks = new_tasks
        ss.crews.append(crew)
        db_utils.save_crew(crew, ss.user_id)
        
        st.success(f"'{data['crew_name']}' Template Imported!")

    def draw(self):
        # Data Loading
        if 'crews' not in ss: ss.crews = db_utils.load_crews(ss.user_id)

        # Header
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h1 style="font-size:48px; margin-bottom:6px; color:#58A6FF;">🧠 Crews</h1>
                <p style="font-size:18px; opacity:0.75;">
                    Orchestrate agents and tasks into a collaborative workflow.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---- TEMPLATE GALLERY ----
        st.markdown("### 🌟 Quickstart Templates")
        t_col1, t_col2, t_col3 = st.columns(3)
        
        with t_col1:
            with st.container(border=True):
                st.markdown("**Web Analyst**")
                st.caption("2 Agents + DuckDuckGo")
                if st.button("Load Web Crew", key="btn_t1"):
                    ss.pending_template = "web_researcher"

        with t_col2:
            with st.container(border=True):
                st.markdown("**Auto-Coder**")
                st.caption("1 Agent + Code Interpreter")
                if st.button("Load Code Crew", key="btn_t2"):
                    ss.pending_template = "coder"

        with t_col3:
            with st.container(border=True):
                st.markdown("**MCP Architect**")
                st.caption("1 Agent + MCP Config")
                if st.button("Load MCP Crew", key="btn_t3"):
                    ss.pending_template = "mcp_expert"

        # Check for pending template applications (This fixes the st.rerun bug)
        if ss.get("pending_template"):
            template_to_apply = ss.pending_template
            ss.pending_template = None # Clear flag
            self.apply_template(template_to_apply)
            st.rerun()

        st.markdown("---")

        # Create Button
        editing = any(crew.edit for crew in ss.crews)
        if st.button("➕ Create Manual Crew", type="primary", disabled=editing):
            self.create_crew()
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Render existing crews
        for crew in ss.crews:
            crew.draw()

        if len(ss.crews) == 0:
            st.info("No crews found. Deploy a template above or create one manually.")