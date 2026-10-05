from fastapi import FastAPI

from backend.schemas import (
    AgentTurnResult,
    ChatRequest,
    HITLDecisionRequest
)
from backend.memory.database import (

    save_message,
    get_conversation_history
)

from backend.agent import agent, run_agent_turn
from backend.memory.memory import get_thread_config
from backend.runtime import resume_turn


app = FastAPI(
    title="Event Discovery AI Assistant"
)


@app.get("/")
def root():
    return {
        "message": "Event Discovery Agent is running"
    }

@app.post("/chat", response_model=AgentTurnResult)
async def chat(request: ChatRequest):
    result = run_agent_turn(
        request.thread_id,
        request.message
    )
    return result

@app.post("/hitl", response_model=AgentTurnResult)
async def hitl_decision(request: HITLDecisionRequest):
    config = get_thread_config(request.thread_id)
    decisions = [
        {
            "type": request.decision
        }
    ]
    result = resume_turn(
        agent,
        decisions,
        config
    )

    if result.text:
        save_message(
            session_id=request.thread_id,
            role="assistant",
            content=result.text
        )
    return result