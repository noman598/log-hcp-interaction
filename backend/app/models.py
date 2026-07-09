"""
Pydantic models for the HCP Interaction Logger.

`InteractionForm` mirrors exactly the fields shown in the left-hand
"Log HCP Interaction" panel in the UI. The AI agent fills these fields
in from free-text chat messages, and the same model is used to persist
a finished interaction to Postgres.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class InteractionForm(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None  # Meeting | Call | Email | Conference
    date: Optional[str] = None              # ISO format YYYY-MM-DD
    time: Optional[str] = None              # e.g. "07:36 PM"
    attendees: List[str] = Field(default_factory=list)
    topics_discussed: Optional[str] = None
    materials_shared: List[str] = Field(default_factory=list)
    samples_distributed: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None         # Positive | Neutral | Negative
    outcomes: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    # The current state of the form as held by the frontend. Sent on every
    # request so the agent can merge new info into what's already there
    # (and so a page refresh / different tab doesn't lose anything).
    current_form: InteractionForm = Field(default_factory=InteractionForm)


class ChatResponse(BaseModel):
    reply: str
    form: InteractionForm


class SaveInteractionRequest(BaseModel):
    session_id: str
    form: InteractionForm


class SaveInteractionResponse(BaseModel):
    id: int
    status: str = "saved"
