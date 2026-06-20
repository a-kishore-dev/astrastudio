import os
import json
import bcrypt
from sqlalchemy import create_engine, text
from datetime import datetime
from cryptography.fernet import Fernet

# Database Configuration
DEFAULT_SQLITE_URL = 'sqlite:///crewai.db'
DB_URL = os.getenv('DB_URL', DEFAULT_SQLITE_URL)
engine = create_engine(DB_URL, echo=False)

def get_db_connection():
    return engine.connect()

def initialize_db():
    with get_db_connection() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT
            )
        '''))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT,
                user_id TEXT,
                entity_type TEXT,
                data TEXT,
                PRIMARY KEY (id, user_id)
            )
        '''))
        conn.commit()

# Initialize Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Fallback for development only - in production, this MUST be in .env
    ENCRYPTION_KEY = Fernet.generate_key().decode() 
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_string(text: str) -> str:
    if not text: return ""
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_string(text: str) -> str:
    if not text: return ""
    try:
        return cipher_suite.decrypt(text.encode()).decode()
    except:
        return "" # Return empty if decryption fails (e.g. key changed)

# --- Credential Specific Persistence ---
def save_user_creds(creds_dict, user_id):
    encrypted = {k: encrypt_string(v) for k, v in creds_dict.items()}
    save_entity('user_credentials', 'vault', encrypted, user_id)

def load_user_creds(user_id):
    rows = load_entities('user_credentials', user_id)
    if not rows: return {}
    return {k: decrypt_string(v) for k, v in rows[0][1].items()}

# --- Auth ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_user(username, password):
    with get_db_connection() as conn:
        res = conn.execute(text("SELECT password_hash FROM users WHERE username = :u"), {"u": username}).fetchone()
        if res and bcrypt.checkpw(password.encode('utf-8'), res[0].encode('utf-8')):
            return True
    return False

def create_user(username, password):
    try:
        with get_db_connection() as conn:
            hashed = hash_password(password)
            conn.execute(text("INSERT INTO users (username, password_hash) VALUES (:u, :p)"), {"u": username, "p": hashed})
            conn.commit()
            return True
    except: return False

# --- Generic Multi-user Scoped CRUD ---
def save_entity(entity_type, entity_id, data, user_id):
    upsert_sql = text('''
        INSERT INTO entities (id, user_id, entity_type, data)
        VALUES (:id, :uid, :etype, :data)
        ON CONFLICT(id, user_id) DO UPDATE SET data = EXCLUDED.data
    ''')
    with get_db_connection() as conn:
        conn.execute(upsert_sql, {"id": entity_id, "uid": user_id, "etype": entity_type, "data": json.dumps(data)})
        conn.commit()

def load_entities(entity_type, user_id):
    query = text('SELECT id, data FROM entities WHERE entity_type = :etype AND user_id = :uid')
    with get_db_connection() as conn:
        result = conn.execute(query, {"etype": entity_type, "uid": user_id})
        rows = result.mappings().all()
    return [(row["id"], json.loads(row["data"])) for row in rows]

def delete_entity(entity_type, entity_id, user_id):
    delete_sql = text('DELETE FROM entities WHERE id = :id AND user_id = :uid AND entity_type = :etype')
    with get_db_connection() as conn:
        conn.execute(delete_sql, {"id": entity_id, "uid": user_id, "etype": entity_type})
        conn.commit()

# --- JSON Export/Import (Scoped to User) ---
def export_to_json(file_path, user_id):
    """Exports all entities belonging ONLY to the current user."""
    with get_db_connection() as conn:
        query = text('SELECT id, entity_type, data FROM entities WHERE user_id = :uid')
        result = conn.execute(query, {"uid": user_id})
        rows = [{"id": r.id, "entity_type": r.entity_type, "data": json.loads(r.data)} for r in result]
        with open(file_path, 'w') as f:
            json.dump(rows, f, indent=4)

def import_from_json(file_path, user_id):
    """Imports entities from JSON and re-assigns them to the current user."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    for entity in data:
        save_entity(entity['entity_type'], entity['id'], entity['data'], user_id)

# --- Specific Model Logic (All verified user-scoped) ---
def save_agent(agent, user_id):
    data = {'created_at': agent.created_at, 'role': agent.role, 'backstory': agent.backstory, 'goal': agent.goal, 'allow_delegation': agent.allow_delegation, 'verbose': agent.verbose, 'cache': agent.cache, 'llm_provider_model': agent.llm_provider_model, 'temperature': agent.temperature, 'max_iter': agent.max_iter, 'tool_ids': [t.tool_id for t in agent.tools], 'knowledge_source_ids': agent.knowledge_source_ids, 'mcp_ids': agent.mcp_ids}
    save_entity('agent', agent.id, data, user_id)

def load_agents(user_id):
    from my_agent import MyAgent
    rows = load_entities('agent', user_id)
    tools_dict = {t.tool_id: t for t in load_tools(user_id)}
    agents = []
    for r in rows:
        d = r[1]
        t_ids = d.pop('tool_ids', [])
        a = MyAgent(id=r[0], **d)
        a.tools = [tools_dict[tid] for tid in t_ids if tid in tools_dict]
        agents.append(a)
    return sorted(agents, key=lambda x: x.created_at)

def delete_agent(agent_id, user_id): delete_entity('agent', agent_id, user_id)

def save_task(task, user_id):
    data = {'description': task.description, 'expected_output': task.expected_output, 'async_execution': task.async_execution, 'agent_id': task.agent.id if task.agent else None, 'context_from_async_tasks_ids': task.context_from_async_tasks_ids, 'context_from_sync_tasks_ids': task.context_from_sync_tasks_ids, 'created_at': task.created_at}
    save_entity('task', task.id, data, user_id)

def load_tasks(user_id):
    from my_task import MyTask
    rows = load_entities('task', user_id)
    agents_dict = {a.id: a for a in load_agents(user_id)}
    tasks = []
    for r in rows:
        d = r[1]
        aid = d.pop('agent_id', None)
        tasks.append(MyTask(id=r[0], agent=agents_dict.get(aid), **d))
    return sorted(tasks, key=lambda x: x.created_at)

def delete_task(task_id, user_id): delete_entity('task', task_id, user_id)

def save_crew(crew, user_id):
    process_val = crew.process.value if hasattr(crew.process, 'value') else str(crew.process).split('.')[-1]
    data = {'name': crew.name, 'process': process_val, 'verbose': crew.verbose, 'agent_ids': [a.id for a in crew.agents], 'task_ids': [t.id for t in crew.tasks], 'memory': crew.memory, 'cache': crew.cache, 'planning': crew.planning, 'planning_llm': crew.planning_llm, 'max_rpm': crew.max_rpm, 'manager_llm': crew.manager_llm, 'manager_agent_id': crew.manager_agent.id if crew.manager_agent else None, 'created_at': crew.created_at, 'knowledge_source_ids': crew.knowledge_source_ids}
    save_entity('crew', crew.id, data, user_id)

def load_crews(user_id):
    from my_crew import MyCrew
    rows = load_entities('crew', user_id)
    agents_dict = {a.id: a for a in load_agents(user_id)}
    tasks_dict = {t.id: t for t in load_tasks(user_id)}
    crews = []
    for r in rows:
        d = r[1]
        c = MyCrew(id=r[0], name=d['name'], process=d['process'], verbose=d['verbose'], created_at=d['created_at'], memory=d.get('memory'), cache=d.get('cache'), planning=d.get('planning'), planning_llm=d.get('planning_llm'), max_rpm=d.get('max_rpm'), manager_llm=d.get('manager_llm'), manager_agent=agents_dict.get(d.get('manager_agent_id')), knowledge_source_ids=d.get('knowledge_source_ids', []))
        c.agents = [agents_dict[aid] for aid in d['agent_ids'] if aid in agents_dict]
        c.tasks = [tasks_dict[tid] for tid in d['task_ids'] if tid in tasks_dict]
        crews.append(c)
    return sorted(crews, key=lambda x: x.created_at)

def delete_crew(crew_id, user_id): delete_entity('crew', crew_id, user_id)

def save_tool(tool, user_id):
    data = {'name': tool.name, 'description': tool.description, 'parameters': tool.get_parameters()}
    save_entity('tool', tool.tool_id, data, user_id)

def load_tools(user_id):
    from my_tools import TOOL_CLASSES
    rows = load_entities('tool', user_id)
    tools = []
    for r in rows:
        d = r[1]
        if d['name'] in TOOL_CLASSES:
            t = TOOL_CLASSES[d['name']](tool_id=r[0]); t.set_parameters(**d['parameters']); tools.append(t)
    return tools

def delete_tool(tool_id, user_id): delete_entity('tool', tool_id, user_id)

def save_tools_state(enabled_tools, user_id):
    save_entity('tools_state', 'enabled_tools', {'enabled_tools': enabled_tools}, user_id)

def load_tools_state(user_id):
    rows = load_entities('tools_state', user_id)
    return rows[0][1].get('enabled_tools', {}) if rows else {}

def save_knowledge_source(ks, user_id):
    data = {'name': ks.name, 'source_type': ks.source_type, 'source_path': ks.source_path, 'content': ks.content, 'metadata': ks.metadata, 'chunk_size': ks.chunk_size, 'chunk_overlap': ks.chunk_overlap, 'created_at': ks.created_at}
    save_entity('knowledge_source', ks.id, data, user_id)

def load_knowledge_sources(user_id):
    from my_knowledge_source import MyKnowledgeSource
    rows = load_entities('knowledge_source', user_id)
    return sorted([MyKnowledgeSource(id=r[0], **r[1]) for r in rows], key=lambda x: x.created_at)

def delete_knowledge_source(ks_id, user_id): delete_entity('knowledge_source', ks_id, user_id)

def save_mcp(mcp, user_id): save_entity("mcp", mcp["id"], mcp, user_id)

def load_mcps(user_id):
    rows = load_entities("mcp", user_id)
    return [{"id": r[0], **r[1]} for r in rows]

def delete_mcp(mcp_id, user_id): delete_entity("mcp", mcp_id, user_id)

def save_result(res, user_id):
    data = {'crew_id': res.crew_id, 'crew_name': res.crew_name, 'inputs': res.inputs, 'result': res.result, 'created_at': res.created_at}
    save_entity('result', res.id, data, user_id)

def load_results(user_id):
    from result import Result
    rows = load_entities('result', user_id)
    return sorted([Result(id=r[0], **r[1]) for r in rows], key=lambda x: x.created_at, reverse=True)

def delete_result(result_id, user_id): delete_entity('result', result_id, user_id)