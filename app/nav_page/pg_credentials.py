import streamlit as st
from streamlit import session_state as ss
import os
import db_utils

CREDENTIAL_FIELDS = {
    "OPENAI_API_KEY": {"secret": True},
    "OPENAI_API_BASE": {"secret": False, "default": "https://api.openai.com/v1/"},
    "GROQ_API_KEY": {"secret": True},
    "GEMINI_API_KEY": {"secret": True},
    "ANTHROPIC_API_KEY": {"secret": True},
    "XAI_API_KEY": {"secret": True},
    "LMSTUDIO_API_BASE": {"secret": False},
    "OLLAMA_HOST": {"secret": False},
}


class PageCredentials:
    def __init__(self):
        self.name = "Credentials"

    def init_session_state(self):
        # 1. First, check if session state is already set
        if "env_vars" not in ss:
            # 2. Try to load from Database (Encrypted)
            db_creds = db_utils.load_user_creds(ss.user_id)
            
            # 3. Fallback to Environment Variables if DB is empty
            ss.env_vars = {}
            for key, cfg in CREDENTIAL_FIELDS.items():
                val = db_creds.get(key) or os.getenv(key, cfg.get("default", ""))
                ss.env_vars[key] = val
            
            ss.credentials_initialized = True

    def apply_and_save_credentials(self):
        # Save to Database (This will trigger encryption in db_utils)
        db_utils.save_user_creds(ss.env_vars, ss.user_id)
        
        # Apply to current environment for immediate use
        for key, value in ss.env_vars.items():
            if value:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

        st.success("Credentials saved to vault and applied for this session.")

    def draw(self):
        self.init_session_state()

        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h1 style="font-size:48px; margin-bottom:6px; color:#58A6FF;">🔐 Credentials</h1>
                <p style="font-size:18px; opacity:0.8;">
                    API keys are <b>AES-encrypted</b> before being stored in the database.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info("Credentials persist across logins and are unique to your account.")

        st.markdown("---")

        # Create a form so we don't save on every keystroke
        with st.form("creds_vault"):
            for key, cfg in CREDENTIAL_FIELDS.items():
                ss.env_vars[key] = st.text_input(
                    label=key,
                    value=ss.env_vars.get(key, ""),
                    type="password" if cfg.get("secret") else "default",
                )
            
            if st.form_submit_button("Save to Vault & Apply", type="primary"):
                self.apply_and_save_credentials()

        if st.button("Clear vault"):
            ss.env_vars = {k: "" for k in CREDENTIAL_FIELDS}
            db_utils.save_user_creds(ss.env_vars, ss.user_id)
            st.rerun()