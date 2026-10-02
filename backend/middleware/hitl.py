from langchain.agents.middleware import HumanInTheLoopMiddleware


def build_hitl_middleware():
    return HumanInTheLoopMiddleware(
        interrupt_on={
            "prepare_booking": {
                "allowed_decisions": ["approve", "reject"]
            },
            
            "search_events_by_location": False,
            "get_event_details": False,
            "get_event_price": False,
        }
    )