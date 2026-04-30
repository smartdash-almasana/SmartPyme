from __future__ import annotations

import sqlite3
from pathlib import Path


class IdentityService:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS onboarding_tokens (
                    token TEXT PRIMARY KEY,
                    cliente_id TEXT NOT NULL,
                    used INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_pairings (
                    telegram_user_id TEXT PRIMARY KEY,
                    cliente_id TEXT NOT NULL
                )
                """
            )

    def create_onboarding_token(self, token: str, cliente_id: str) -> None:
        if not token or not token.strip():
            raise ValueError("token is required")
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO onboarding_tokens (token, cliente_id, used)
                VALUES (?, ?, 0)
                ON CONFLICT(token) DO UPDATE SET
                    cliente_id = excluded.cliente_id,
                    used = 0
                """,
                (token, cliente_id),
            )

    def link_telegram_user(self, telegram_user_id: str | int, token: str) -> dict:
        user_id = str(telegram_user_id)
        if not user_id or not user_id.strip():
            raise ValueError("telegram_user_id is required")
        if not token or not token.strip():
            raise ValueError("token is required")

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT token, cliente_id, used FROM onboarding_tokens WHERE token = ?",
                (token,),
            ).fetchone()

            if row is None or row["used"] == 1:
                return {
                    "status": "invalid_token",
                    "telegram_user_id": user_id,
                    "cliente_id": None,
                }

            cliente_id = row["cliente_id"]
            conn.execute(
                """
                INSERT INTO telegram_pairings (telegram_user_id, cliente_id)
                VALUES (?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    cliente_id = excluded.cliente_id
                """,
                (user_id, cliente_id),
            )
            conn.execute(
                "UPDATE onboarding_tokens SET used = 1 WHERE token = ?",
                (token,),
            )

        return {
            "status": "linked",
            "telegram_user_id": user_id,
            "cliente_id": cliente_id,
        }

    def get_cliente_id_for_telegram_user(self, telegram_user_id: str | int) -> str | None:
        user_id = str(telegram_user_id)
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT cliente_id FROM telegram_pairings WHERE telegram_user_id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return row["cliente_id"]

    def is_authorized(self, telegram_user_id: str | int) -> bool:
        return self.get_cliente_id_for_telegram_user(telegram_user_id) is not None

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
