"""
Very small, dependency-light Postgres helper.

This is intentionally simple (plain psycopg + raw SQL, no ORM, no
migrations, no connection pool) because this project is a demo, not a
production service. Swap in SQLAlchemy/Alembic if this ever needs to grow.
"""
import json
import os

import psycopg
from psycopg.rows import dict_row

PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "hcp_logger")
PG_USER = os.getenv("POSTGRES_USER", "hcp_user")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hcp_pass")


def get_connection():
    return psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        # Optional: Auto-commit mode if you want
        # autocommit=True,
    )


def init_db():
    """Create the interactions table if it doesn't already exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    form_data JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


def save_interaction(session_id: str, form_data: dict) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO interactions (session_id, form_data)
                VALUES (%s, %s)
                RETURNING id;
                """,
                (session_id, json.dumps(form_data)),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def list_interactions(limit: int = 50):
    conn = get_connection()
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, session_id, form_data, created_at
                FROM interactions
                ORDER BY created_at DESC
                LIMIT %s;
                """,
                (limit,),
            )
            return cur.fetchall()
    finally:
        conn.close()
