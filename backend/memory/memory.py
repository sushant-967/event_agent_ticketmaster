
from langgraph.checkpoint.sqlite import SqliteSaver

# Persistent SQLite checkpoint database
DB_PATH = "agent_checkpoints.db"

# Keep the SQLite connection open
checkpointer_context = SqliteSaver.from_conn_string(DB_PATH)

checkpointer = checkpointer_context.__enter__()

# Thread configuration
def get_thread_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id
        }
    }