import os
import sqlite3
import json
from typing import Any, Dict, List, Optional


class Database:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self._ensure()

    def _ensure(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    text TEXT,
                    quizzes TEXT,
                    readability TEXT,
                    glossary TEXT
                );
                """
            )

    def save_session(self, text: str, quizzes: List[Dict[str, Any]], readability: Dict[str, Any], glossary: Dict[str, Any]) -> int:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO sessions(text, quizzes, readability, glossary) VALUES (?,?,?,?)",
                (text, json.dumps(quizzes), json.dumps(readability), json.dumps(glossary)),
            )
            conn.commit()
            return cur.lastrowid

    def list_sessions(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT id, created_at FROM sessions ORDER BY id DESC").fetchall()
            return [{"id": r["id"], "created_at": r["created_at"]} for r in rows]

    def load_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "created_at": row["created_at"],
                "text": row["text"],
                "quizzes": json.loads(row["quizzes"] or "[]"),
                "readability": json.loads(row["readability"] or "{}"),
                "glossary": json.loads(row["glossary"] or "{}"),
            }

