
from pydantic import BaseModel,Field
from typing import Any, Optional,Literal
from dataclasses import dataclass

class ChatRequest(BaseModel):
    message:str
    thread_id:str="default-session"

class ChatResponse(BaseModel):
    response: str
    requires_approval: bool = False
    approval_data: Optional[dict] = None


class TurnSummary(BaseModel):
    """What the coding agent did in this turn?"""
    summary:str=Field(description="A concise summary of what the coding agent did in this turn")

    files_touched:list[str]=Field(
        description="Relative paths of the file you read,created or edited",
        default_factory=list
    )

    status: Literal["ok","needs_input","failed"]|None=Field(
        description="ok if the request is done , needs_input if you must ask user, failed if the request failed"
    )


@dataclass
class AgentTurnResult:
    text: str
    structured: TurnSummary | None
    messages: list[Any]
    pending_interrupt: dict[str, Any] | None


class HITLDecisionRequest(BaseModel):
    thread_id: str
    decision: Literal["approve", "reject"]