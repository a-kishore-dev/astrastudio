<h1 align="center">
  <img src="img/icon.png" alt="Astrastudio Logo" width="45" style="vertical-align: middle; margin-right: 8px;" />
  Astrastudio
</h1>

<p align="center">
  <b>A Secure, Multi-User Collaborative AI Agent Workspace built on CrewAI and Streamlit.</b>
</p>

<p align="center">
  <a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+" /></a>
  <a href="https://streamlit.io" target="_blank"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit" /></a>
  <a href="https://github.com/crewAIInc/crewAI" target="_blank"><img src="https://img.shields.io/badge/CrewAI-Multi--Agent-7c3aed" alt="CrewAI" /></a>
  <a href="https://www.sqlalchemy.org/" target="_blank"><img src="https://img.shields.io/badge/SQLAlchemy-ORM-d71f00" alt="SQLAlchemy" /></a>
  <a href="LICENSE" target="_blank"><img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="MIT License" /></a>
</p>

<p align="center">
  <a href="https://github.com/strnad/CrewAI-Studio" target="_blank"><img src="https://img.shields.io/badge/Based%20on-strnad%2FCrewAI--Studio-181717?logo=github&logoColor=white" alt="Based on CrewAI-Studio" /></a>
</p>

Astrastudio is an enterprise-grade, low-code visual IDE and orchestration platform designed to build, run, test, and observe collaborative Multi-Agent AI crews. It wraps the powerful [CrewAI](https://github.com/crewAIInc/crewAI) agent framework in an intuitive, multi-user web interface powered by [Streamlit](https://streamlit.io).

> **Built on [`strnad/CrewAI-Studio`](https://github.com/strnad/CrewAI-Studio) (MIT License).** Astrastudio takes that project's no-code agent/task/crew builder as its foundation and extends it with multi-user authentication, an encrypted credentials vault, DocLing-powered knowledge ingestion, an MCP server hub with pre-flight connection testing, dependency-aware cascade deletion, and a redesigned interface. See [Relationship to CrewAI-Studio](#-relationship-to-crewai-studio) for the full breakdown of what's inherited vs. new.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://astrastudio.streamlit.app/) 

---

## 📋 Table of Contents

- [Relationship to CrewAI-Studio](#-relationship-to-crewai-studio)
- [Visual Preview](#-visual-preview)
- [Key Enhancements](#-key-enhancements-whats-new-in-astrastudio)
- [Architecture](#️-architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Quickstart Crew Templates](#-quickstart-crew-templates)
- [Supported LLM Providers](#supported-llm-providers)
- [Available Agent Tools](#available-agent-tools)
- [Model Context Protocol (MCP)](#model-context-protocol-mcp)
- [Knowledge Sources](#knowledge-sources)
- [Export & Deployment Options](#export--deployment-options)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🔗 Relationship to CrewAI-Studio

Astrastudio is a fork of [`strnad/CrewAI-Studio`](https://github.com/strnad/CrewAI-Studio), an MIT-licensed, no-code GUI for managing and running CrewAI agents. The table below separates what Astrastudio inherits from that base from what's been added on top.

| Capability                                                                   | CrewAI-Studio (upstream) |                     Astrastudio (this project)                     |
| ---------------------------------------------------------------------------- | :----------------------: | :----------------------------------------------------------------: |
| No-code Agent / Task / Crew builder                                          |            ✅            |                            ✅ Inherited                            |
| Multi-provider LLM support (OpenAI, Groq, Anthropic, Ollama, xAI, LM Studio) |            ✅            |                  ✅ Inherited, plus Google Gemini                  |
| Custom tools (API calls, file writing, enhanced scraper/code interpreter)    |            ✅            |                            ✅ Inherited                            |
| Single-page app export & threaded crew execution (run/stop)                  |            ✅            |   ✅ Inherited, extended with full-workspace and per-crew export   |
| Multi-user authentication & per-user data isolation                          |            —             | ✅ **New** — Bcrypt signup/login, all entities scoped to `user_id` |
| Encrypted credentials vault                                                  |            —             | ✅ **New** — Fernet-encrypted at rest, swept from memory on logout |
| DocLing-powered knowledge ingestion (URLs, complex docs)                     |            —             |                             ✅ **New**                             |
| MCP server hub with pre-flight connection testing                            |            —             |     ✅ **New** — handshake + tool discovery before a crew runs     |
| Dependency-aware cascade deletion dialogs                                    |            —             |         ✅ **New** — `st.dialog`-based conflict resolution         |
| Quickstart crew templates (Web Analyst, Auto-Coder, MCP Architect)           |            —             |                             ✅ **New**                             |
| Cyber Blue UI theme                                                          |            —             |                             ✅ **New**                             |

_Rows marked "—" reflect functionality not present in the upstream project's documented feature set at the time of forking; this is not a claim about CrewAI-Studio's current state, which may have evolved since._

All credit for the original architecture, domain model design, and CrewAI integration patterns goes to [Jakub Strnad](https://github.com/strnad) and the CrewAI-Studio contributors. See [License](#license) for attribution requirements.

---

## 🎨 Visual Preview

Screenshots below follow the app's actual sidebar navigation order: **Home → Crews → Tools → Agents → Tasks → MCP → Knowledge → Kickoff! → Results → Credentials**.

| Page / Functionality                              | Screenshot                                     |
| ------------------------------------------------- | ---------------------------------------------- |
| **Login / Sign Up**                               | ![Login Screen](img/login_page.png)            |
| **Workspace Home**                                | ![Workspace Home](img/home_page.png)           |
| **Crews — Quickstart Templates & Manual Builder** | ![Crew Builder](img/crews_page.png)            |
| **Tools Registry**                                | ![Tools Registry](img/tools_page.png)          |
| **Agent Studio (List View)**                      | ![Agent Builder](img/agent_page.png)           |
| **Agent Details & Configuration**                 | ![Agent Details](img/agent_details.png)        |
| **Task Management (List View)**                   | ![Task Planner](img/task_page.png)             |
| **Task Detail Drill-down**                        | ![Task Detail](img/tool_details.png)           |
| **MCP Server Hub**                                | ![MCP Hub](img/mcp_page.png)                   |
| **Knowledge Base Ingestion**                      | ![Knowledge Base](img/knowledge_page.png)      |
| **Kickoff! — Run a Crew**                         | ![Crew Kickoff](img/kickoff_page.png)          |
| **Results — Per-Task Breakdown**                  | ![Task Results](img/sample_output1.png)        |
| **Results — Final Output**                        | ![Final Output](img/sample_output.png)         |
| **Results — Run History**                         | ![Results Page](img/results_page.png)          |
| **Credentials Vault**                             | ![Credentials Vault](img/credentials_page.png) |

---

## 🚀 Key Enhancements (What's New in Astrastudio)

Astrastudio evolves the original `CrewAI-Studio` codebase into a secure, multi-tenant environment with robust diagnostic and validation systems:

1. **Multi-User Isolation & Authentication**
   - **Bcrypt Authentication**: Features a complete signup and login system to protect user access.
   - **Workspace Isolation**: Scopes all database entities—agents, tasks, crews, tools, custom parameters, knowledge sources, and execution results—specifically to the logged-in `user_id`.

2. **Secure Credentials Vault (Fernet Encrypted)**
   - Avoid hardcoding sensitive API keys. Use the **Credentials** page to manage tokens dynamically.
   - Keys are encrypted in the SQL database using **Fernet symmetric encryption** (`cryptography`) and loaded directly into active environment variables (`os.environ`) for the current session. All credentials are swept from memory on logout.

3. **Advanced Knowledge Base (DocLing & Local File Uploads)**
   - **Document Parsers**: Directly upload PDFs, Text files, CSV, Excel, and JSON files to a local `knowledge/` folder using the UI.
   - **DocLing Ingestion**: Integrated the `DocLing` engine to parse web URLs and complex document structures into clean, chunkable text.
   - **Granular Controls**: Custom chunk sizes and chunk overlaps configurable per source (defaults: chunk size `4000`, chunk overlap `200`).

4. **Model Context Protocol (MCP) Server Hub & Pre-Flight Connection Tester**
   - Connect agents to custom tool and data integrations using **HTTP**, **SSE**, or **stdio** transport layers.
   - Features a **Pre-Flight Test Connection** utility in the UI that connects to the MCP server, performs the tool handshake, pings endpoints, and displays the discovered tools to verify integrity before launching a crew run.

5. **Dependency Analysis & Cascade Deletion Dialogs**
   - Implemented a smart deletion workflow using Streamlit's dialog system (`st.dialog`).
   - When deleting a crew, Astrastudio automatically inspects the dependency graph to determine if any associated agents or tasks are shared with other crews, or if tasks are referenced as context dependencies.
   - Displays warnings and conflicts visually, giving the choice to **Delete Crew Only**, **Cancel**, or **Delete Crew + Selected Items** (cascading).

6. **Quickstart Crew Templates**
   - The Crews page ships with one-click starter templates — **Web Analyst** (2 agents + DuckDuckGo search), **Auto-Coder** (1 agent + Code Interpreter), and **MCP Architect** (1 agent + MCP config) — alongside the option to build a crew manually from scratch.

7. **Cyber Blue Premium Theme & UX Polishing**
   - Replaced standard Streamlit styling with a curated dark-mode theme featuring modern colors, hover shadows, and custom layouts.

---

## 🏗️ Architecture

Astrastudio sits on top of the CrewAI multi-agent framework, storing agent topologies in a relational database mapping back to the Streamlit UI layer. The diagram below traces a request from sign-in through to persistence:

```mermaid
flowchart TD
    Start([Start])
    End([End])

    Vault[/Secure Credentials Vault/]
    MCPHub[/MCP Server Hub/]
    MultiUser[/Multi-User Isolation/]
    Knowledge[/Knowledge Base DocLing/]

    UI["Astrastudio UI — app/app.py
    Dashboard, Agent Editor, MCP Testbed, Credentials Vault
    Streamlit Web Interface"]

    Session["Authenticated Session State
    user_id scope · Bcrypt Auth"]

    Domain["Domain Models — my_*.py
    MyAgent ➔ MyTask ➔ MyCrew ➔ crewai.Crew.kickoff()
    CrewAI Integration Layer"]

    Persist[/"SQL Persistence — db_utils.py & LLM Layer
    SQLite (default) or PostgreSQL via DB_URL
    Encrypted Storage & AI Providers · Fernet Encryption"/]

    Start --> UI
    Vault --> UI
    MCPHub --> UI
    MultiUser --> UI

    UI -- "User Context" --> Session
    Session -- "Session data" --> UI

    Session -- "Bidirectional" --> Domain
    Domain -- "Domain results" --> Session

    Knowledge --> Domain

    Domain -- "Bidirectional" --> Persist
    Persist -- "Persist / load" --> Domain

    Persist --> End

    classDef terminal fill:#a7e8c8,stroke:#2f9e62,stroke-width:1.5px,color:#0a3622
    classDef io fill:#b9d4f5,stroke:#3a6fb0,stroke-width:1.5px,color:#0a2a4d
    classDef process fill:#fdf3b0,stroke:#cdae1e,stroke-width:1.5px,color:#3d3208
    classDef persistNode fill:#fdf3b0,stroke:#cdae1e,stroke-width:1.5px,color:#3d3208

    class Start,End terminal
    class Vault,MCPHub,MultiUser,Knowledge io
    class UI,Session,Domain process
    class Persist persistNode
```

**Reading the flow:** the **Secure Credentials Vault**, **MCP Server Hub**, and **Multi-User Isolation** layer all feed into the Streamlit UI as it boots. Once a request carries a `user_id`, the **Authenticated Session State** exchanges `User Context` down and `Session data` back up with the UI. From there, the **Domain Models** layer (`MyAgent ➔ MyTask ➔ MyCrew ➔ crewai.Crew.kickoff()`) bidirectionally exchanges data with the session and pulls in **Knowledge Base (DocLing)** sources directly. Finally, the **SQL Persistence & LLM layer** (SQLite or PostgreSQL, Fernet-encrypted) handles `Persist / load` for everything the Domain Models layer needs to read or write.

---

## Features

Astrastudio provides full visual control over your agent workflows:

- **No-Code Visual Editors**: Add, modify, and delete agents, tasks, and tools without touching Python code.
- **Hierarchical or Sequential Processing**: Coordinate crews via structured workflows or manager LLMs/agents.
- **Context Chaining**: Feed results from previous synchronous or asynchronous tasks directly into downstream tasks.
- **Execution Capturing**: Capture terminal output live, display custom spinner indicators, and stop long-running operations.
- **Persisted History & Reports**: View outputs, download HTML execution reports, and analyze historic crew runs.

---

## Prerequisites

- **Python 3.10** or later (Python 3.11+ recommended).
- **pip** (Python package installer).
- **Docker** (optional; required for sandboxed python code execution via `CodeInterpreterTool`).

---

## Installation

1. **Clone the repository**:

   ```bash
   git clone astrastudio
   cd Astrastudio
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   _Note: Installs may take several minutes as it configures ML dependencies, document parsers, and LLM clients._

4. **Set up the Environment variables**:
   ```bash
   cp .env.example .env  # If not present, create a `.env` manually.
   ```

---

## Configuration

Create a `.env` file in the root directory. You can set base keys here, or let users configure them on the **Credentials** page inside the UI.

### System Variables

| Variable         | Description                                                                                                                                                                                                                                                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DB_URL`         | SQLAlchemy Connection String. Defaults to SQLite: `sqlite:///crewai.db`. For production, configure PostgreSQL: `postgresql://user:pass@host:5432/dbname`.                                                                                                             |
| `ENCRYPTION_KEY` | Fernet key for encrypting credentials in the DB. If not set, a temporary key is generated on launch (causes credentials to clear if server restarts). Generate a key via: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

### LLM Providers

| Variable            | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| `OPENAI_API_KEY`    | OpenAI API key.                                              |
| `OPENAI_API_BASE`   | OpenAI-compatible custom endpoint URL (e.g. for Local LLMs). |
| `GEMINI_API_KEY`    | Google Gemini API key.                                       |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key.                                    |
| `GROQ_API_KEY`      | Groq API key.                                                |
| `XAI_API_KEY`       | xAI (Grok) API key.                                          |
| `OLLAMA_HOST`       | Ollama service endpoint.                                     |
| `LMSTUDIO_API_BASE` | Local LM Studio endpoint (e.g. `http://localhost:1234/v1`).  |

> ⚠️ **Security note:** `ENCRYPTION_KEY` should be generated once and kept stable across restarts. If it's left unset, a new key is generated on every launch and previously stored credentials become undecryptable — every user would need to re-enter their API keys.

---

## Running the Application

Launch the Streamlit dashboard from the **project root folder**:

```bash
streamlit run app/app.py
```

The app opens automatically in your browser (default: `http://localhost:8501`).

---

## Usage Guide

1. **Sign Up & Log In**: Create an isolated database partition for yourself.
2. **Setup Credentials**: Enter the API keys for the models you want to use.
3. **Equip Tools**: Enable and pre-configure standard search and scraping tools.
4. **Draft Agents**: Give agents a `Role`, `Backstory`, and `Goal`, plus fine-grained controls — `Allow delegation`, `Verbose`, `Cache`, `LLM Provider and Model`, `Temperature`, `Max Iterations`, and assigned `Tools`.
5. **Assign Tasks**: Write a `Description` and `Expected output`, assign the responsible `Agent`, toggle `Async execution`, and optionally chain in `Context from async/sync tasks`.
6. **Form Crews**: Pack tasks and agents together, select a process mechanism, and toggle planning phases — or start from a **Quickstart Template** (see below).
7. **Kickoff**: Enter dynamic prompt parameters (`{placeholders}` in task descriptions) and run your crew.
8. **View Results**: Dig into per-task outputs and the final combined output, then export printable reports.

---

## ⚡ Quickstart Crew Templates

For a faster start than building a crew from scratch, the **Crews** page offers one-click templates:

| Template          | Composition                  | Use Case                                                        |
| ----------------- | ---------------------------- | --------------------------------------------------------------- |
| **Web Analyst**   | 2 Agents + DuckDuckGo search | Research and synthesize information from the open web           |
| **Auto-Coder**    | 1 Agent + Code Interpreter   | Generate and execute Python in a sandboxed environment          |
| **MCP Architect** | 1 Agent + MCP Config         | Bootstrap an agent pre-wired to a Model Context Protocol server |

Click **Load Web Crew**, **Load Code Crew**, or **Load MCP Crew** to instantiate one, or use **Create Manual Crew** to build from an empty canvas.

---

## Supported LLM Providers

| Provider          | Example Models                                  | Format                                |
| ----------------- | ----------------------------------------------- | ------------------------------------- |
| **Google Gemini** | `gemini-2.5-flash`, `gemini-2.5-pro`            | `Gemini: gemini-2.5-flash`            |
| **OpenAI**        | `gpt-4o-mini`, `gpt-4o`, `o1-mini`              | `OpenAI: gpt-4o-mini`                 |
| **Anthropic**     | `claude-3-5-sonnet-latest`                      | `Anthropic: claude-3-5-sonnet-latest` |
| **Groq**          | `llama-3.3-70b-versatile`, `mixtral-8x7b-32768` | `Groq: llama-3.3-70b-versatile`       |
| **xAI**           | `grok-2-1212`, `grok-beta`                      | `xAI: grok-2-1212`                    |
| **Ollama**        | Custom local models (e.g. `llama3`)             | Configured via `OLLAMA_MODELS`        |
| **LM Studio**     | Local models                                    | OpenAI-compatible endpoint            |

---

## Available Agent Tools

Astrastudio comes pre-bundled with 30+ tools classified into logical blocks:

### 🔎 Internet & Financial Search

- `DuckDuckGoSearchTool`: Standard free search without API keys.
- `SerperDevTool`: Google Search powered by Serper API.
- `EXASearchTool`: Context-aware search engine integrations.
- `YahooFinanceNewsTool`: Financial market search queries.

### 🌐 Advanced Scraping & Web APIs

- `ScrapeWebsiteTool`: Standard webpage scraper.
- `ScrapeWebsiteToolEnhanced`: Supports CSS selectors, cookies, and URLs.
- `ScrapflyScrapeWebsiteTool`: Scrapfly proxy, anti-bot bypass, and headless browser.
- `SeleniumScrapingTool`: Chrome-automated Selenium scraping.
- `ScrapeElementFromWebsiteTool`: Target specific elements using CSS class/ID.
- `CustomApiTool`: Configure and run HTTP queries dynamically.

### 📂 Document & Semantic Code Finders

- `FileReadTool` / `CustomFileWriteTool`: Text read/write tools.
- `DirectorySearchTool` / `DirectoryReadTool`: Search directories.
- `PDFSearchTool` / `DOCXSearchTool` / `CSVSearchToolEnhanced` / `JSONSearchTool` / `MDXSearchTool`: Vector semantic index search inside files.
- `GithubSearchTool`: Scan repositories for files, PRs, and issues.
- `CodeDocsSearchTool`: Vector database search over code documentation.

### 🐚 Sandboxed Code Interpreters

- `CodeInterpreterTool`: Executes agent-generated Python in a secure sandboxed Docker container.
- `CustomCodeInterpreterTool`: Runs code with access to shared workspace directories.

---

## Model Context Protocol (MCP)

To connect agents with local filesystems, database adapters, and developer endpoints:

1. Head to the **MCP** tab.
2. Select your server transport type:
   - **HTTP/SSE**: Input endpoint URLs and secure authorization headers (JSON).
   - **stdio**: Input local node or python terminal scripts (e.g. `npx -y @modelcontextprotocol/server-filesystem /path/to/shared-folder`).
3. Click **Test connection** to trigger pre-flight handshakes and check discovered tools.
4. Assign the MCP profile to any Agent inside the **Agents** tab.

The MCP page surfaces what these servers unlock at a glance: **remote tools and actions**, **external data sources**, and **shared context across agents**.

---

## Knowledge Sources

Astrastudio links contextual domain-specific knowledge to agents using CrewAI's RAG pipeline:

- **Text String**: Add raw inline notes and instructions.
- **Text File**: Load local `.txt` documents.
- **Structured Data**: Read PDF, CSV, Excel, and JSON datasets.
- **DocLing Ingestor**: Converts complex files and online page paths into markdown tables and text blocks.

Each source supports configurable chunking — the default is **chunk size `4000`** with **chunk overlap `200`**, adjustable per source. Upload files directly into the **Knowledge** page to save them in the `knowledge/` workspace directory, or use **Clear All Knowledge Stores** to reset.

---

## Export & Deployment Options

Astrastudio handles backups and productionizing crews in three ways:

1. **Full Workspace Backup**: Export all agents, tasks, crews, and configurations to a single user-scoped JSON.
2. **Individual Crew Export**: Save a single crew profile and its dependencies to import elsewhere.
3. **Standalone App Generator**: Generates a `.zip` package containing a standalone Streamlit app representing the crew:
   - Self-contained `app.py`.
   - Complete `requirements.txt`.
   - `install.sh` / `.bat` and `run.sh` / `.bat` startup files.
   - Customized environment variables template `.env`.

These are accessible from the **Import/export** tab in the sidebar.

---

## Project Structure

```
Astrastudio/
├── app/
│   ├── app.py                  # Main entry point & routing configuration
│   ├── llms.py                 # LLM engine mappings and custom model clients
│   ├── db_utils.py             # User authentication & database operations (SQLAlchemy)
│   ├── my_agent.py             # MyAgent wrapper class
│   ├── my_task.py              # MyTask wrapper class
│   ├── my_crew.py              # MyCrew builder with dependency resolution
│   ├── my_tools.py             # Registered tools mapping & creation logic
│   ├── my_knowledge_source.py  # Knowledge structures (DocLing, Pandas, text)
│   ├── mcp_utils.py            # Model Context Protocol parsing & connections
│   ├── console_capture.py      # capture stdout live output to show on UI
│   ├── utils.py                # Formatting and cross-platform UI adjustments
│   ├── result.py               # Result metadata schema
│   ├── nav_page/               # Streamlit page modules
│   │   ├── pg_home.py          # Dashboard homepage
│   │   ├── pg_credentials.py  # Encrypted credentials vault
│   │   ├── pg_agents.py        # Agent creator UI
│   │   ├── pg_tasks.py         # Task configuration UI
│   │   ├── pg_crews.py         # Crew constructor UI
│   │   ├── pg_tools.py         # Custom tools UI
│   │   ├── pg_knowledge.py     # RAG sources & files UI
│   │   ├── pg_mcp.py           # MCP configuration UI
│   │   ├── pg_crew_run.py      # Execution monitor (Kickoff!)
│   │   └── pg_results.py       # Historically saved run result viewer
│   └── tools/                  # Custom agent tool classes (Scrapfly, Api, CSV)
├── img/                        # Branding assets and interface screenshot folder
├── knowledge/                  # Local knowledge files store (dynamically populated)
├── tests/                      # Unit tests
├── requirements.txt            # System dependencies
├── pyproject.toml              # Project metadata and lint configs
└── crewai.db                   # SQLite database (defaults here if DB_URL is empty)
```

---

## Troubleshooting

| Error                           | Cause                                           | Action                                                                                                                                            |
| ------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Database Lock / Errors**      | Corrupt database or SQLite threading conflicts. | Remove local `crewai.db` to recreate, or configure a `DB_URL` pointing to PostgreSQL.                                                             |
| **Fernet Decryption Failures**  | Changing the `ENCRYPTION_KEY` in `.env`         | Re-enter credentials on the credentials page, or generate and save a static `ENCRYPTION_KEY` in `.env`.                                           |
| **Docker Tool Execution Error** | Docker daemon is stopped or not installed.      | Start your Docker Desktop runtime environment before using `CodeInterpreterTool`.                                                                 |
| **MCP Stdio failures**          | Cloud environment restricts stdio.              | Standard local transport (`stdio`) requires process isolation. Host your app locally or transition to remote HTTP/SSE servers on Cloud Streamlit. |
| **Missing LLM Providers**       | API key not provided or misspelled names.       | Navigate to the **Credentials** page or check `.env` parameter namespaces.                                                                        |

---

## License

Astrastudio is released under the **MIT License**, consistent with the upstream [`CrewAI-Studio`](https://github.com/strnad/CrewAI-Studio) project it extends (Copyright © 2024 Jakub Strnad). The original copyright and permission notice is preserved per the MIT License's terms; see [`LICENSE`](LICENSE) for the full text.

---

## 🙏 Acknowledgements

- **[Jakub Strnad](https://github.com/strnad)** and the [`CrewAI-Studio`](https://github.com/strnad/CrewAI-Studio) contributors — original architecture, domain model, and CrewAI integration this project is built on
- **[CrewAI](https://github.com/crewAIInc/crewAI)** — the underlying multi-agent orchestration framework
- **[Streamlit](https://streamlit.io)** — the web framework powering the UI
- **[DocLing](https://github.com/DS4SD/docling)** — document and URL ingestion for the Knowledge Base
- **`cryptography` (Fernet)** — credential encryption at rest
