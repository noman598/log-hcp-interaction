"""
FastAPI entrypoint for the HCP Interaction Logger demo backend.

Run with:
    uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agent import run_agent
from app.db import init_db, list_interactions, save_interaction
from app.models import (
    ChatRequest,
    ChatResponse,
    InteractionForm,
    SaveInteractionRequest,
    SaveInteractionResponse,
)

app = FastAPI(title="HCP Interaction Logger (Demo)")

# Wide-open CORS for local demo purposes only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as exc:  # pragma: no cover - demo-friendly startup log
        print(f"[startup] Could not initialize Postgres (is it running?): {exc}")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Takes the rep's free-text message + the form state the frontend
    currently holds, runs it through the LangGraph agent, and returns an
    updated form plus a conversational reply.
    """
    try:
        reply, updated_form = run_agent(req.message, req.current_form.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}")

    return ChatResponse(reply=reply, form=InteractionForm(**updated_form))


@app.post("/api/interactions", response_model=SaveInteractionResponse)
def create_interaction(req: SaveInteractionRequest):
    try:
        new_id = save_interaction(req.session_id, req.form.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DB error: {exc}")
    return SaveInteractionResponse(id=new_id)


@app.get("/api/interactions")
def get_interactions(limit: int = 50):
    try:
        return list_interactions(limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DB error: {exc}")
