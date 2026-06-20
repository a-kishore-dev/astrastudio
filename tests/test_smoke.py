#!/usr/bin/env python3
"""Smoke tests for Astrastudio modules (run from project root)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-smoke-tests")


def test_mcp_utils():
    from mcp_utils import mcp_entry_to_crewai_config, build_agent_mcps, parse_stdio_command
    from crewai.mcp import MCPServerHTTP, MCPServerSSE, MCPServerStdio

    command, args = parse_stdio_command("npx -y @modelcontextprotocol/server-filesystem /data")
    assert command == "npx"
    assert args == ["-y", "@modelcontextprotocol/server-filesystem", "/data"]

    http_cfg = mcp_entry_to_crewai_config({
        "name": "remote",
        "type": "http",
        "endpoint": "https://example.com/mcp",
        "enabled": True,
    })
    assert isinstance(http_cfg, MCPServerHTTP)
    assert http_cfg.url == "https://example.com/mcp"

    sse_cfg = mcp_entry_to_crewai_config({
        "name": "stream",
        "type": "sse",
        "endpoint": "https://example.com/mcp/sse",
        "enabled": True,
    })
    assert isinstance(sse_cfg, MCPServerSSE)

    stdio_cfg = mcp_entry_to_crewai_config({
        "name": "local",
        "type": "stdio",
        "command": "python3 server.py",
        "enabled": True,
    })
    assert isinstance(stdio_cfg, MCPServerStdio)
    assert stdio_cfg.command == "python3"
    assert stdio_cfg.args == ["server.py"]

    disabled = build_agent_mcps([
        {"name": "off", "type": "http", "endpoint": "https://example.com/mcp", "enabled": False},
        {"name": "on", "type": "http", "endpoint": "https://example.com/mcp", "enabled": True},
    ])
    assert len(disabled) == 1

    from crewai import Agent
    agent = Agent(
        role="Tester",
        goal="Validate MCP wiring",
        backstory="Test agent",
        mcps=disabled,
        llm="gpt-4o-mini",
    )
    assert agent.mcps is not None
    print("PASS: mcp_utils")


def test_my_agent_uses_mcps():
    import streamlit as st
    from my_agent import MyAgent
    from crewai.mcp import MCPServerHTTP

    if not hasattr(st, "session_state"):
        st.session_state = st.runtime.state.session_state_proxy.SessionStateProxy()

    ss = st.session_state
    ss.clear()
    ss.mcps = [{
        "id": "mcp_test",
        "name": "Test MCP",
        "type": "http",
        "endpoint": "https://example.com/mcp",
        "enabled": True,
    }]
    ss.knowledge_sources = []
    ss.tools = []
    ss.env_vars = {"OPENAI_API_KEY": "test-key", "OPENAI_API_BASE": "https://api.openai.com/v1/"}
    ss.credentials_initialized = True

    agent = MyAgent(mcp_ids=["mcp_test"], llm_provider_model="OpenAI: gpt-4o-mini")
    crewai_agent = agent.get_crewai_agent()
    assert crewai_agent.mcps is not None
    assert isinstance(crewai_agent.mcps[0], MCPServerHTTP)
    print("PASS: my_agent MCP integration")


def test_github_tool():
    from my_tools import MyGithubSearchTool

    tool = MyGithubSearchTool(gh_token="token", content_types="code,issue")
    assert tool.parameters.get("content_types") == "code,issue"
    # Avoid instantiating crewai GithubSearchTool here — qdrant_client version
    # mismatches in minimal test envs are unrelated to Astrastudio wiring.
    print("PASS: github tool content_types parameter")


def test_db_roundtrip():
    import db_utils
    from my_agent import MyAgent

    db_utils.initialize_db()
    mcp = {
        "id": "mcp_db_test",
        "name": "DB MCP",
        "type": "http",
        "endpoint": "https://example.com/mcp",
        "headers": "Authorization: Bearer test",
        "enabled": True,
    }
    db_utils.save_mcp(mcp, ss.user_id)
    loaded = db_utils.load_mcps(ss.user_id)
    assert any(item["id"] == "mcp_db_test" for item in loaded)
    db_utils.delete_mcp("mcp_db_test", ss.user_id)
    print("PASS: db MCP roundtrip")


def test_imports():
    modules = [
        "db_utils", "llms", "my_agent", "my_task", "my_crew", "my_tools",
        "my_knowledge_source", "result", "utils", "console_capture", "mcp_utils",
        "nav_page.pg_home", "nav_page.pg_agents", "nav_page.pg_tasks",
        "nav_page.pg_crews", "nav_page.pg_tools", "nav_page.pg_mcp",
        "nav_page.pg_knowledge", "nav_page.pg_crew_run", "nav_page.pg_results",
        "nav_page.pg_export_crew", "nav_page.pg_credentials",
    ]
    for module in modules:
        __import__(module)
    print(f"PASS: imported {len(modules)} modules")


if __name__ == "__main__":
    tests = [
        test_imports,
        test_mcp_utils,
        test_db_roundtrip,
        test_github_tool,
        test_my_agent_uses_mcps,
    ]
    failed = []
    for test in tests:
        try:
            test()
        except Exception as exc:
            failed.append((test.__name__, exc))
            print(f"FAIL: {test.__name__}: {exc}")

    if failed:
        print(f"\n{len(failed)} test(s) failed")
        sys.exit(1)
    print(f"\nAll {len(tests)} tests passed")
