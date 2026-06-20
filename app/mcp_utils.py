import os
import json
import shlex
import streamlit as st
import requests  # Added for pre-flight check
from typing import Any
from crewai.mcp import MCPServerHTTP, MCPServerSSE, MCPServerStdio

def parse_stdio_command(command_line: str) -> tuple[str, list[str]]:
    parts = shlex.split(command_line.strip())
    if not parts: return "node", []
    return parts[0], parts[1:]

def mcp_entry_to_crewai_config(mcp: dict[str, Any]):
    transport = (mcp.get("type") or "http").lower()
    headers = None
    if mcp.get("headers"):
        try: headers = json.loads(mcp["headers"])
        except: headers = {}

    if transport == "stdio":
        cmd, args = parse_stdio_command(mcp.get("command", ""))
        return MCPServerStdio(command=cmd, args=args)
    
    endpoint = (mcp.get("endpoint") or "").strip()
    if transport == "sse":
        return MCPServerSSE(url=endpoint, headers=headers)
    return MCPServerHTTP(url=endpoint, headers=headers, streamable=True)

def test_mcp_connection(mcp: dict[str, Any]) -> tuple[bool, str]:
    from crewai import Agent
    from llms import create_llm

    try:
        # 1. Environment Sync
        env_vars = st.session_state.get("env_vars", {})
        os.environ["OPENAI_API_KEY"] = env_vars.get("OPENAI_API_KEY") or "sk-placeholder"
        
        if env_vars.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = env_vars["GEMINI_API_KEY"]
            selected_model = "Gemini: gemini-1.5-flash"
        else:
            return False, "Gemini API Key is required in Credentials page."

        # 2. Pre-flight Check (Only for HTTP/SSE)
        if mcp.get("type") in ["http", "sse"]:
            url = mcp.get("endpoint", "")
            try:
                # Try to see if the server is even awake
                requests.get(url, timeout=3)
            except Exception:
                return False, f"Network Error: Cannot reach {url}. Ensure the server is running and reachable from your browser."

        # 3. CrewAI Test
        test_llm = create_llm(selected_model)
        agent = Agent(role="Tester", goal="Test", backstory="Test", llm=test_llm)
        config = mcp_entry_to_crewai_config(mcp)
        
        # We wrap this specific call because this is where CrewAI 1.5.0 has the bug
        try:
            discovered_tools = agent.get_mcp_tools([config])
        except Exception as e:
            if "tools_list" in str(e):
                return False, "Server reached, but tool handshake failed. This often happens if the MCP server version is incompatible or returns an invalid schema."
            return False, f"CrewAI Error: {str(e)}"

        if not discovered_tools:
            return True, "Connected! But the server reports 0 available tools."
            
        return True, f"Connected! Found {len(discovered_tools)} tools: {', '.join([t.name for t in discovered_tools[:3]])}..."

    except Exception as e:
        return False, f"System Error: {str(e)}"

def build_agent_mcps(mcp_entries: list[dict[str, Any]]) -> list[Any]:
    return [mcp_entry_to_crewai_config(m) for m in mcp_entries if m.get("enabled", True)]