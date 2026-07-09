"""
LangGraph agent that turns a free-text rep note (e.g. "Met Dr. Smith,
discussed Prodo-X efficacy, positive sentiment, shared brochure") into
structured updates for the InteractionForm, plus a short conversational
reply shown back in the chat panel.

Design (kept intentionally small for a demo):

    START -> extract -> END

The single "extract" node calls Claude once, asking it to return the
message reply that will be shown to the user AND ONLY the fields it can
confidently infer from the latest message (everything else is left
null / empty). The FastAPI layer then merges those fields on top of the
form state the frontend already has, so information from earlier
messages is never lost.
"""
import os
from typing import List, Optional, TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from app.models import InteractionForm

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "gemma2-9b-it")

MODEL_NAME = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")


class ExtractedFields(BaseModel):
    """Same shape as InteractionForm, but every field is optional and the
    model is instructed to leave anything unmentioned as null/empty so we
    can safely merge it into the existing form state."""

    hcp_name: Optional[str] = Field(default=None, description="Name of the healthcare professional, if mentioned")
    interaction_type: Optional[str] = Field(default=None, description="One of: Meeting, Call, Email, Conference")
    date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format, if mentioned")
    time: Optional[str] = Field(default=None, description="Time in 'hh:mm AM/PM' format, if mentioned")
    attendees: List[str] = Field(default_factory=list, description="Names of people who attended, other than the HCP")
    topics_discussed: Optional[str] = Field(default=None, description="Short summary of topics discussed")
    materials_shared: List[str] = Field(default_factory=list, description="Materials/brochures shared, e.g. ['Brochures']")
    samples_distributed: List[str] = Field(default_factory=list, description="Product samples given to the HCP")
    sentiment: Optional[str] = Field(default=None, description="One of: Positive, Neutral, Negative")
    outcomes: Optional[str] = Field(default=None, description="Key outcomes or agreements reached")


class AgentReply(BaseModel):
    reply: str = Field(description="A short, friendly acknowledgement of what was logged, 1-2 sentences.")
    fields: ExtractedFields


class AgentState(TypedDict):
    user_message: str
    current_form: dict
    reply: str
    updated_form: dict


SYSTEM_PROMPT = """You are an assistant embedded in a pharma CRM tool that helps a sales rep
log a Healthcare Professional (HCP) interaction by chatting in plain English.

The rep will describe an interaction, e.g.:
"Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure"

Extract only what is explicitly stated or can be safely and confidently
inferred from THIS message. Do not invent facts. Do not repeat values that
would just duplicate what's already in the existing form unless the user is
correcting or adding to them. Leave a field empty/null if it isn't mentioned.

interaction_type must be one of: Meeting, Call, Email, Conference (default to
"Meeting" only if the message clearly describes an in-person/virtual meeting
and no type is otherwise implied).
sentiment must be one of: Positive, Neutral, Negative.

Also write a short (1-2 sentence) natural, friendly reply confirming what you
just logged, as if you're a helpful assistant chatting with the rep.
"""


def build_agent():
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0,
        # Optional: Add these for better structured output
        # model_kwargs={"response_format": {"type": "json_object"}}
    )
    structured_llm = llm.with_structured_output(AgentReply)

    def extract_node(state: AgentState) -> AgentState:
        current_form = InteractionForm(**state["current_form"])
        prompt = (
            f"Existing form state so far (JSON): {current_form.model_dump_json()}\n\n"
            f"Rep's new message: \"{state['user_message']}\"\n\n"
            "Return the reply and the newly extracted fields from this message only."
        )
        result: AgentReply = structured_llm.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
        )

        merged = current_form.model_dump()
        new_fields = result.fields.model_dump()
        for key, value in new_fields.items():
            if value in (None, "", []):
                continue
            if isinstance(value, list):
                # Merge lists without duplicates, preserving order.
                existing = merged.get(key) or []
                merged[key] = existing + [v for v in value if v not in existing]
            else:
                merged[key] = value

        return {
            **state,
            "reply": result.reply,
            "updated_form": merged,
        }

    graph = StateGraph(AgentState)
    graph.add_node("extract", extract_node)
    graph.add_edge(START, "extract")
    graph.add_edge("extract", END)
    return graph.compile()


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def run_agent(user_message: str, current_form: dict):
    agent = get_agent()
    result = agent.invoke({"user_message": user_message, "current_form": current_form})
    return result["reply"], result["updated_form"]
