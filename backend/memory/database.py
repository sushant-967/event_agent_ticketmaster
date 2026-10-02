
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


# Database location
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "conversation_memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the conversation history table."""

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id
            ON conversations(session_id)
        """)

        conn.commit()


def save_message(session_id: str, role: str, content: str):
    """Persist a single conversation message."""

    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversations
            (session_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, timestamp)
        )

        conn.commit()


def get_conversation_history(session_id: str):
    """Retrieve conversation history for a session."""

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT role, content
            FROM conversations
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,)
        )

        rows = cursor.fetchall()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]


def clear_conversation(session_id: str):
    """Delete conversation history for a session."""

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM conversations WHERE session_id = ?",
            (session_id,)
        )

        conn.commit()