
from langgraph.checkpoint.sqlite import SqliteSaver

# Persistent SQLite checkpoint database
DB_PATH = "agent_checkpoints.db"

# Keep the SQLite connection open
checkpointer_context = SqliteSaver.from_conn_string(DB_PATH)

checkpointer = checkpointer_context.__enter__()

# Thread configuration
thread_config = {
    "configurable": {
        "thread_id": "ticketmate-session"
    }
}