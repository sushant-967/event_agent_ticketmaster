from langchain_groq import ChatGroq
from langchain.agents import create_agent
from backend.memory.memory import checkpointer,thread_config
from backend.config import GROQ_API_KEY
from backend.tools.ticketmaster import (
    search_events_by_location,
    get_event_details,
    get_event_price
)

from typing import Any
from backend.runtime import start_turn, resume_turn
from backend.runtime import AgentTurnResult, format_interrupt
from backend.tools.booking import prepare_booking
from backend.runtime import AgentTurnResult,format_interrupt
from backend.middleware.hitl import build_hitl_middleware

SYSTEM_PROMPT = """
You are an intelligent event discovery assistant.

Your job is to help users discover real events using Ticketmaster.

Rules:

1. Always use Ticketmaster tools for event information.
2. Never invent event data.
3. Never invent prices.
4. Maintain conversational context.
5. If the user refers to an event number such as "the second event",
   use the previous search results.
6. Ask clarification if location or date is ambiguous.
7. For booking requests, always require human approval.
8. Never directly purchase tickets.
9. Return clear, concise responses.
"""



model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY
)

ALL_TOOLS = [
    search_events_by_location,
    get_event_details,
    get_event_price,
    prepare_booking
]


agent = create_agent(
    model=model,
    tools=ALL_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    middleware=[
        build_hitl_middleware(),
    ],
    checkpointer=checkpointer
)
config=thread_config


def _prompt_decision(pending: dict[str,Any])->list[dict]:
    print("\n--------------Human in the loop-----",flush=True)
    print(pending)
    choice = input("choice: ").strip().lower()

    if choice not in {"approve", "reject"}:
        raise ValueError("Enter approve or reject")

    return [{"type": choice}]
    # print(format_interrupt(pending),flush=True)
    # requests=pending.get("action_requests") or []
    # decisions: list[dict]=[]


    
def _drain(agent,result:AgentTurnResult,config:config):
    while result.pending_interrupt is not None:
        decision=_prompt_decision(result.pending_interrupt)
        result=resume_turn(agent,decision,config)
    return result

print("\n🎟️ Welcome to TicketMate AI Assistant!")
print("Hello! 👋 How can I help you today?\n")
print("Type exit or q or quit to stop.")
while True:
    user_input=input("You: ").strip()
    if user_input.lower() in {"exit","q","quit"}:
        break
    if not user_input:
        continue
    result=_drain(agent,start_turn(agent,user_input,config),config)
    print(result.text)
    
    
    
    
final_response = result.text
print("\nAgent Response:")
print(final_response)
