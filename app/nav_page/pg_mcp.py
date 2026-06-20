import streamlit as st
from streamlit import session_state as ss
from utils import rnd_id
import db_utils
from mcp_utils import mcp_entry_to_crewai_config, test_mcp_connection


class PageMCP:
    def __init__(self):
        self.name = "MCP"

    def init_state(self):
        if "mcps" not in ss:
            ss.mcps = db_utils.load_mcps(ss.user_id)

    def add_mcp(self, name, mcp_type, endpoint, command, headers):
        mcp = {
            "id": f"mcp_{rnd_id()}",
            "name": name,
            "type": mcp_type,
            "endpoint": endpoint,
            "command": command,
            "headers": headers,
            "enabled": True,
        }
        try:
            mcp_entry_to_crewai_config(mcp)
        except Exception as exc:
            st.error(f"Invalid MCP configuration: {exc}")
            return False

        ss.mcps.append(mcp)
        db_utils.save_mcp(mcp, ss.user_id)
        return True

    def update_mcp_enabled(self, mcp_id):
        enabled = ss.get(f"enabled_{mcp_id}", True)
        for mcp in ss.mcps:
            if mcp["id"] == mcp_id:
                mcp["enabled"] = enabled
                # Add user_id
                db_utils.save_mcp(mcp, ss.user_id)
                break

    def remove_mcp(self, mcp_id):
        ss.mcps = [m for m in ss.mcps if m["id"] != mcp_id]
        db_utils.delete_mcp(mcp_id, ss.user_id)
        st.rerun()

    def draw(self):
        self.init_state()

        st.markdown(
            """
            <div style="margin-bottom:20px;">
                <h1 style="font-size:48px; margin-bottom:6px;">MCP</h1>
                <p style="font-size:18px; opacity:0.75;">
                    Connect agents to external Model Context Protocol (MCP) servers.
                    MCP servers provide tools, resources, and prompts beyond local capabilities.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                border-radius:12px;
                padding:14px 16px;
                border:1px solid rgba(255,255,255,0.08);
                background:rgba(255,255,255,0.02);
                max-width:500px;
                margin-bottom:24px;
                font-size:18px;
            ">
                <strong>What MCP provides</strong>
                <ul style="margin-top:8px; padding-left:18px;">
                    <li>Remote tools and actions</li>
                    <li>External data sources</li>
                    <li>Shared context across agents</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### Add MCP server")

        name = st.text_input("Name")
        mcp_type = st.selectbox("Transport", ["http", "sse", "stdio"])

        endpoint = None
        command = None
        headers = None

        if mcp_type in ("http", "sse"):
            endpoint = st.text_input(
                "Server URL",
                placeholder="https://api.example.com/mcp",
                help="Use HTTPS for remote servers. HTTP localhost URLs are supported via structured transport.",
            )
            headers = st.text_area(
                "Headers (optional)",
                placeholder='Authorization: Bearer your-token',
                help="One header per line (Key: Value) or JSON object.",
            )
        else:
            command = st.text_input(
                "Command",
                placeholder="npx -y @modelcontextprotocol/server-filesystem /data",
                help="Full shell command. The first token is the executable; remaining tokens are arguments.",
            )

        if st.button("➕ Add MCP server", disabled=not name):
            if self.add_mcp(name, mcp_type, endpoint, command, headers):
                st.success(f"Added MCP server '{name}'.")
                st.rerun()

        st.markdown("---")
        st.markdown("### Enabled MCP servers")

        if not ss.mcps:
            st.info("No MCP servers configured.")
            return

        for mcp in ss.mcps:
            with st.expander(mcp["name"], expanded=not mcp["enabled"]):
                st.write(f"**Type:** {mcp['type']}")
                if mcp.get("endpoint"):
                    st.code(mcp["endpoint"])
                if mcp.get("command"):
                    st.code(mcp["command"])
                if mcp.get("headers"):
                    st.markdown("**Headers:**")
                    st.code(mcp["headers"])

                try:
                    preview = mcp_entry_to_crewai_config(mcp)
                    st.caption(f"CrewAI config: {preview.__class__.__name__}")
                except Exception as exc:
                    st.warning(f"Configuration issue: {exc}")

                if st.button("Test connection", key=f"test_{mcp['id']}"):
                    with st.spinner("Testing MCP connection..."):
                        ok, message = test_mcp_connection(mcp)
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)

                st.checkbox(
                    "Enabled",
                    value=mcp["enabled"],
                    key=f"enabled_{mcp['id']}",
                    on_change=self.update_mcp_enabled,
                    args=(mcp["id"],),
                )

                if st.button("🗑 Remove MCP", key=f"remove_{mcp['id']}"):
                    self.remove_mcp(mcp["id"])
