"""Telegram handler mínimo: allowlist, dedup y callback token table."""
from __future__ import annotations

import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("data/telegram_control.db")


def _conn(path: str | Path = DB_PATH) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS processed_updates (update_id INTEGER PRIMARY KEY, command TEXT, processed_at TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS callback_tokens (callback_id TEXT PRIMARY KEY, cycle_id TEXT NOT NULL, action TEXT NOT NULL, expires_at TEXT NOT NULL)"
    )
    conn.commit()
    return conn


def is_allowed_user(from_user_id: int, allowed_user_ids: list[int]) -> bool:
    return int(from_user_id) in {int(item) for item in allowed_user_ids}


def mark_update_processed(update_id: int, command: str = "", db_path: str | Path = DB_PATH) -> bool:
    conn = _conn(db_path)
    try:
        conn.execute(
            "INSERT INTO processed_updates(update_id, command, processed_at) VALUES (?, ?, ?)",
            (int(update_id), command, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def create_callback_token(cycle_id: str, action: str, ttl_seconds: int = 300, db_path: str | Path = DB_PATH) -> str:
    callback_id = secrets.token_urlsafe(16)
    assert len(callback_id.encode("utf-8")) <= 64
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    conn = _conn(db_path)
    conn.execute(
        "INSERT INTO callback_tokens(callback_id, cycle_id, action, expires_at) VALUES (?, ?, ?, ?)",
        (callback_id, cycle_id, action, expires_at.isoformat()),
    )
    conn.commit()
    conn.close()
    return callback_id


def resolve_callback_token(callback_id: str, db_path: str | Path = DB_PATH) -> dict[str, Any] | None:
    conn = _conn(db_path)
    row = conn.execute(
        "SELECT cycle_id, action, expires_at FROM callback_tokens WHERE callback_id = ?",
        (callback_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    expires_at = datetime.fromisoformat(row[2])
    if datetime.now(timezone.utc) > expires_at:
        return None
    return {"cycle_id": row[0], "action": row[1], "expires_at": row[2]}
