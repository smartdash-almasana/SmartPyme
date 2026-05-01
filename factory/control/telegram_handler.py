"""Telegram control primitives for SmartPyme Factory v2.1.

This module is deliberately small and deterministic:
- allowlist by from_user.id;
- update_id deduplication;
- callback token table with callback_data <= 64 bytes;
- no network calls;
- no secrets in repo.
"""
from __future__ import annotations

import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

DB_PATH = Path("data/telegram_control.db")
ALLOWLIST_PATH = Path("factory/ai_governance/telegram_allowlist.yaml")


def _conn(path: str | Path = DB_PATH) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        (
            "CREATE TABLE IF NOT EXISTS processed_updates "
            "(update_id INTEGER PRIMARY KEY, command TEXT, processed_at TEXT NOT NULL)"
        )
    )
    conn.execute(
        (
            "CREATE TABLE IF NOT EXISTS callback_tokens "
            "(callback_id TEXT PRIMARY KEY, cycle_id TEXT NOT NULL, "
            "action TEXT NOT NULL, expires_at TEXT NOT NULL)"
        )
    )
    conn.commit()
    return conn


def load_allowed_user_ids(path: str | Path = ALLOWLIST_PATH) -> list[int]:
    source = Path(path)
    if not source.exists():
        return []
    payload = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    ids: list[int] = []
    owner = payload.get("owner") or {}
    if owner.get("enabled", True) and int(owner.get("user_id", 0) or 0) > 0:
        ids.append(int(owner["user_id"]))
    for group in ("moderators", "auditors"):
        for item in payload.get(group) or []:
            if item.get("enabled", True) and int(item.get("user_id", 0) or 0) > 0:
                ids.append(int(item["user_id"]))
    return sorted(set(ids))


def is_allowed_user(
    from_user_id: int,
    allowed_user_ids: list[int] | None = None,
    allowlist_path: str | Path = ALLOWLIST_PATH,
) -> bool:
    ids = (
        allowed_user_ids
        if allowed_user_ids is not None
        else load_allowed_user_ids(allowlist_path)
    )
    return int(from_user_id) in {int(item) for item in ids}


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


def create_callback_token(
    cycle_id: str,
    action: str,
    ttl_seconds: int = 300,
    db_path: str | Path = DB_PATH,
) -> str:
    callback_id = secrets.token_urlsafe(16)
    if len(callback_id.encode("utf-8")) > 64:
        raise ValueError("callback_data exceeds Telegram 64-byte limit")
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    conn = _conn(db_path)
    conn.execute(
        (
            "INSERT INTO callback_tokens(callback_id, cycle_id, action, expires_at) "
            "VALUES (?, ?, ?, ?)"
        ),
        (callback_id, cycle_id, action, expires_at.isoformat()),
    )
    conn.commit()
    conn.close()
    return callback_id


def resolve_callback_token(
    callback_id: str,
    db_path: str | Path = DB_PATH,
) -> dict[str, Any] | None:
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


def validate_update(
    update: dict[str, Any],
    db_path: str | Path = DB_PATH,
    allowlist_path: str | Path = ALLOWLIST_PATH,
) -> dict[str, Any]:
    """Validate a Telegram update without executing side effects beyond dedup storage."""
    update_id = int(update.get("update_id", -1))
    message = update.get("message") or update.get("callback_query", {}).get("message") or {}
    from_user = (
        update.get("message", {}).get("from")
        or update.get("callback_query", {}).get("from")
        or {}
    )
    user_id = int(from_user.get("id", 0) or 0)
    text = str(
        update.get("message", {}).get("text")
        or update.get("callback_query", {}).get("data")
        or ""
    )

    if not is_allowed_user(user_id, allowlist_path=allowlist_path):
        return {"status": "error", "code": "UNAUTHORIZED", "message": "Usuario no autorizado"}
    if not mark_update_processed(update_id, text, db_path=db_path):
        return {"status": "ignored", "code": "DUPLICATE_UPDATE", "message": "Update ya procesado"}
    return {
        "status": "ok",
        "code": "ACCEPTED",
        "message": "Update aceptado",
        "command": text,
        "chat_id": message.get("chat", {}).get("id"),
    }
