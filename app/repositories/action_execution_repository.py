from __future__ import annotations

import sqlite3
from pathlib import Path

from app.contracts.execution_adapter_contract import ExecutionAdapterResult


class ActionExecutionRepository:
    """Minimal SQLite repository for adapter execution results."""

    def __init__(self, db_path: str | Path) -> None:
        path = Path(db_path)
        if not str(path).strip():
            raise ValueError("db_path is required")
        if path.is_dir():
            raise ValueError("db_path must be a file path, not a directory")

        self._db_path = path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def save(self, result: ExecutionAdapterResult) -> None:
        if not isinstance(result, ExecutionAdapterResult):
            raise ValueError("result must be ExecutionAdapterResult")

        payload = result.traceable_origin or {}
        payload_json = _to_json(payload)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO action_execution_results (
                    adapter_id,
                    action_id,
                    status,
                    message,
                    traceable_origin
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    result.adapter_id,
                    result.action_id,
                    result.status,
                    result.message,
                    payload_json,
                ),
            )
            conn.commit()

    def list_results(self, action_id: str | None = None) -> list[ExecutionAdapterResult]:
        if action_id is not None and not action_id.strip():
            raise ValueError("action_id must not be blank when provided")

        query = """
            SELECT adapter_id, action_id, status, message, traceable_origin
            FROM action_execution_results
        """
        params: tuple[str, ...] = ()
        if action_id is not None:
            query += " WHERE action_id = ?"
            params = (action_id,)
        query += " ORDER BY id ASC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            ExecutionAdapterResult(
                adapter_id=row[0],
                action_id=row[1],
                status=row[2],
                message=row[3],
                traceable_origin=_from_json(row[4]),
            )
            for row in rows
        ]

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS action_execution_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adapter_id TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    traceable_origin TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_action_execution_results_action_id
                ON action_execution_results(action_id)
                """
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def _to_json(value: dict) -> str:
    import json

    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _from_json(value: str) -> dict:
    import json

    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("traceable_origin must deserialize to dict")
    return data
