from langgraph.checkpoint.memory import InMemorySaver

# Checkpointer for saving agent execution state
checkpointer = InMemorySaver()

# Thread configuration
thread_config = {
    "configurable": {
        "thread_id": "ticketmate-session"
    }
}