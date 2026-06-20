import streamlit as st
from streamlit import session_state as ss
import db_utils
from nav_page.pg_home import PageHome
from nav_page.pg_agents import PageAgents
from nav_page.pg_tasks import PageTasks
from nav_page.pg_crews import PageCrews
from nav_page.pg_tools import PageTools
from nav_page.pg_mcp import PageMCP
from nav_page.pg_crew_run import PageCrewRun
from nav_page.pg_export_crew import PageExportCrew
from nav_page.pg_results import PageResults
from nav_page.pg_knowledge import PageKnowledge
from nav_page.pg_credentials import PageCredentials
from nav_page.pg_credentials import CREDENTIAL_FIELDS 
from dotenv import load_dotenv
from llms import load_secrets_fron_env
import os
import time
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def pages():
    return {
        'Home': PageHome(),
        'Crews': PageCrews(),
        'Tools': PageTools(),
        'Agents': PageAgents(),
        'Tasks': PageTasks(),
        'MCP': PageMCP(),
        'Knowledge': PageKnowledge(),
        'Kickoff!': PageCrewRun(),
        'Results': PageResults(),
        'Import/export': PageExportCrew(),
        'Credentials': PageCredentials(),
    }

PAGE_ICONS = {
    "Home": "🏠", "Crews": "🧠", "Tools": "🛠️", "Agents": "🤖",
    "Tasks": "📝", "MCP": "🔗", "Knowledge": "📚", "Kickoff!": "🚀",
    "Results": "📊", "Import/export": "📦", "Credentials": "🔐",
}

def load_data():
    if "user_id" in ss:
        uid = ss.user_id
        ss.agents = db_utils.load_agents(uid)
        ss.tasks = db_utils.load_tasks(uid)
        ss.crews = db_utils.load_crews(uid)
        ss.tools = db_utils.load_tools(uid)
        ss.enabled_tools = db_utils.load_tools_state(uid)
        ss.knowledge_sources = db_utils.load_knowledge_sources(uid)
        ss.mcps = db_utils.load_mcps(uid)

def login_page():
    try:
        logo_base64 = get_base64_image("img/icon.png") 
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="80" style="vertical-align: middle; margin-right: 15px;">'
    except Exception:
        logo_html = ""

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                {logo_html}
                <h1 style="color: #58A6FF; margin: 0; font-size: 42px;">Astrastudio</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if db_utils.verify_user(u, p):
                        ss.logged_in = True
                        ss.user_id = u
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        with tab2:
            with st.form("signup_form"):
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                confirm_p = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if new_p != confirm_p:
                        st.error("Passwords do not match")
                    elif len(new_p) < 4:
                        st.error("Password must be at least 4 characters")
                    elif db_utils.create_user(new_u, new_p):
                        st.success(f"Account created for {new_u}!")
                        ss.logged_in = True
                        ss.user_id = new_u
                        time.sleep(1)
                        st.rerun()
                        # -------------------------
                    else:
                        st.error("Username already taken")

def draw_sidebar():
    with st.sidebar:
        st.image("img/logo.png", use_container_width=True)
        st.markdown(f"<h3 style='text-align: center; color: #58A6FF;'>User: {ss.user_id}</h3>", unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear() 

            for key in CREDENTIAL_FIELDS:
                if key in os.environ:
                    del os.environ[key]

            for key in list(ss.keys()):
                del ss[key]
                
            st.rerun()
            
        st.markdown("---")

        if "page" not in ss:
            ss.page = "Home"

        for page_name in pages().keys():
            icon = PAGE_ICONS.get(page_name, "•")
            is_active = ss.page == page_name

            if st.button(
                f"{icon}  {page_name}",
                key=f"nav-{page_name}",
                width="stretch",
                type="primary" if is_active else "secondary",
            ):
                ss.page = page_name
                st.rerun()

def main():
    st.set_page_config(page_title="Astrastudio", page_icon="img/icon.png", layout="wide")
    
    # Professional Cyber Blue Theme
    st.markdown("""
        <style>
            .stApp { background-color: #0D1117; color: #C9D1D9; }
            [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
            .stButton>button { background-color: #1D7AFC; color: white; border: none; border-radius: 4px; }
            .stButton>button:hover { background-color: #388BFD; box-shadow: 0 0 10px rgba(56, 139, 253, 0.4); }
            h1, h2, h3 { color: #58A6FF !important; }
            div[data-testid="stExpander"] { background-color: #161B22 !important; border: 1px solid #30363D !important; }
            .stMarkdown, .stAlert, div[data-testid="stExpander"] div {
                white-space: normal !important;
                word-wrap: break-word !important;
                overflow-wrap: break-word !important;
            }

            .stMarkdown p {
                line-height: 1.6 !important;
                margin-bottom: 1rem !important;
            }
            
            code {
                white-space: pre-wrap !important;
            }
        </style>
    """, unsafe_allow_html=True)

    load_dotenv()
    load_secrets_fron_env()
    db_utils.initialize_db()

    # Authentication Check
    if "logged_in" not in ss:
        ss.logged_in = False

    if not ss.logged_in:
        login_page()
        return # STOP HERE if not logged in

    # If logged in, show the app
    if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
        try:
            import agentops
            agentops.init(api_key=os.getenv('AGENTOPS_API_KEY'), auto_start_session=False)    
        except ModuleNotFoundError:
            ss.agentops_failed = True
            
    load_data()
    user_creds = db_utils.load_user_creds(ss.user_id)
    for key, value in user_creds.items():
        if value: os.environ[key] = value
    draw_sidebar()
    PageCrewRun.maintain_session_state() 
    pages()[ss.page].draw()
    
if __name__ == '__main__':
    main()