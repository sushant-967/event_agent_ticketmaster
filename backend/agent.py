from langchain_groq import ChatGroq
from langchain.agents import create_agent
from backend.memory.memory import checkpointer,thread_config
from backend.config import GROQ_API_KEY
from backend.tools.ticketmaster import (
    search_events_by_location,
    get_event_details,
    get_event_price
)

from backend.memory.database import (
    initialize_database,
    save_message,
    get_conversation_history
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
10. If a booking tool call is rejected by the human reviewer,
    do not retry the booking tool.

11. Treat a rejected booking request as final for the current turn.

12. Never attempt another booking after receiving a rejection
    unless the user explicitly initiates a new booking request.
"""

# Initialize SQLite database
initialize_database()
config=thread_config
# Use the same session ID as LangGraph
session_id = config["configurable"]["thread_id"]


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




def _prompt_decision(pending: dict[str, Any]) -> list[dict]:

    print("\n-------------- Human in the Loop --------------")
    print(format_interrupt(pending))

    while True:

        choice = input(
            "\nEnter approve or reject: "
        ).strip().lower()

        if choice == "approve":
            print("Explicit approval received.")
            return [{"type": "approve"}]

        elif choice == "reject":
            print("Booking request rejected.")
            return [{"type": "reject"}]

        else:
            print(
                "Invalid input. No action was approved. "
                "Please enter approve or reject."
            )

    

def _drain(agent, result: AgentTurnResult, config: dict):

    booking_rejected = False
    max_interrupts = 3
    interrupt_count = 0

    while result.pending_interrupt is not None:

        interrupt_count += 1

        if interrupt_count > max_interrupts:
            print(
                "Maximum interrupt limit reached. "
                "Stopping automatic execution."
            )
            return result

        pending = result.pending_interrupt

        if booking_rejected:

            print(
                "\nBooking was already rejected. "
                "Automatically rejecting subsequent tool requests."
            )

            decision = [{"type": "reject"}]

        else:

            decision = _prompt_decision(pending)

            if decision[0]["type"] == "reject":
                booking_rejected = True

                print(
                    "\nBooking rejected. "
                    "No further booking approval will be granted "
                    "during this turn."
                )

        result = resume_turn(
            agent,
            decision,
            config
        )

    return result

print("\n🎟️ Welcome to TicketMate AI Assistant!")
print("Hello! 👋 How can I help you today?\n")
print("Type exit or q or quit to stop.")

session_id = config["configurable"]["thread_id"]

history = get_conversation_history(session_id)

print("\nPrevious Conversation:")

for message in history:
    print(f"{message['role']}: {message['content']}")
while True:
    user_input=input("You: ").strip()
    if user_input.lower() in {"exit","q","quit"}:
        break
    if not user_input:
        continue
    
    # 1. Persist user message
    save_message(
        session_id=session_id,
        role="user",
        content=user_input
    )

    result=_drain(agent,start_turn(agent,user_input,config),config)
    print(result.text)
    # 4. Persist assistant response
    if result.text:
        save_message(
            session_id=session_id,
            role="assistant",
            content=result.text
        )

    
    
    
    
final_response = result.text
print("\nAgent Response:")
print(final_response)
