# HCP Interaction Logger (Demo)

A small demo app that lets a pharma sales rep describe an HCP (Healthcare
Professional) interaction in plain English in a chat panel, and has an
LLM agent (via LangGraph + Claude) fill in the structured "Log HCP
Interaction" form on the left in real time.

This is built for a demo / prototype, not production:
- No auth, no multi-user support, no migrations, in-memory session on the frontend only.
- CORS wide open, single Postgres table, no connection pooling.
- Keep this in mind before deploying it anywhere real.

## Stack

- **Frontend:** React (Vite), plain CSS - no UI framework, kept simple.
- **Backend:** FastAPI (Python).
- **AI agent:** LangGraph + `langchain-anthropic` (Claude) - one-node graph
  that extracts structured fields from each chat message and merges them
  into the existing form state.
- **DB:** Postgres (a single `interactions` table storing the saved form as JSONB).

## Project layout

```
hcp-interaction-logger/
├── docker-compose.yml        # spins up Postgres only
├── backend/
│   ├── main.py                # FastAPI app + routes
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── models.py          # Pydantic schemas (InteractionForm, chat req/resp)
│       ├── db.py               # psycopg2 helpers (init/save/list)
│       └── agent.py            # LangGraph agent (extraction + merge logic)
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx             # wires form + chat together, holds shared state
        ├── api.js               # fetch helpers for the backend
        ├── emptyForm.js
        ├── index.css
        └── components/
            ├── LogForm.jsx      # left-hand form panel
            ├── ChatPanel.jsx    # right-hand AI assistant chat panel
            └── ChipList.jsx     # reusable tag input (attendees/materials/samples)
```

## Setup

### 1. Postgres

```bash
docker compose up -d
```

This starts Postgres on `localhost:5432` with db `hcp_logger`, user
`hcp_user`, password `hcp_pass` (matches `backend/.env.example`). No
Docker? Just point the `POSTGRES_*` env vars at any Postgres instance
you already have.

### 2. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...
uvicorn main:app --reload --port 8000
```

The table is created automatically on startup (`init_db()` in `db.py`).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

## How it works

1. The rep types something like:
   > "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure"
   in the chat box on the right and hits Enter / the send button.
2. The frontend POSTs `{ session_id, message, current_form }` to `POST /api/chat`.
3. The backend runs a LangGraph graph (`app/agent.py`) with a single node
   that calls Claude with structured output, asking it to extract only
   the fields implied by this message (leaving everything else null), plus
   a short natural-language reply.
4. The backend merges the newly extracted fields on top of `current_form`
   (list fields like `attendees` / `materials_shared` / `samples_distributed`
   are appended to, not replaced) and returns `{ reply, form }`.
5. The frontend replaces its form state with the returned `form`, so every
   field in the left panel updates live, and shows `reply` as a new chat bubble.
6. Clicking **Save Interaction** POSTs the current form to
   `POST /api/interactions`, which inserts it as a JSONB row in Postgres.

Fields can also be edited directly in the form (it's a normal controlled
form) - the chat is just an alternate, faster way to fill it in.

## Extending this later

- Add authentication + per-user sessions instead of the single frontend-held session id.
- Replace the raw-SQL `db.py` with SQLAlchemy + Alembic migrations.
- Add a `GET /api/interactions/{id}` + edit view, and wire `Search/Add` for
  materials/samples to a real product catalog instead of free-text chips.
- Expand the LangGraph graph with a validation node (e.g., checking the
  HCP name against a real HCP directory) before merging fields.
