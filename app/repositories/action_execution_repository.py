from __future__ import annotations

import sqlite3
from pathlib import Path

from app.contracts.execution_adapter_contract import ExecutionAdapterResult


class ActionExecutionRepository:
    def __init__(self, cliente_id: str, db_path: str | Path) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required for ActionExecutionRepository")

        self.cliente_id = cliente_id
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS action_execution_results (
                    cliente_id TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    adapter_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    traceable_origin_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_action_exec_cliente_action
                ON action_execution_results(cliente_id, action_id)
                """
            )

    def save(self, result: ExecutionAdapterResult) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO action_execution_results (
                    cliente_id,
                    action_id,
                    adapter_id,
                    status,
                    message,
                    traceable_origin_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    self.cliente_id,
                    result.action_id,
                    result.adapter_id,
                    result.status,
                    result.message,
                    str(result.traceable_origin),
                ),
            )

    def list_results(self, action_id: str | None = None) -> list[ExecutionAdapterResult]:
        query = """
            SELECT action_id, adapter_id, status, message
            FROM action_execution_results
            WHERE cliente_id = ?
              AND (? IS NULL OR action_id = ?)
            ORDER BY created_at ASC
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (self.cliente_id, action_id, action_id)).fetchall()

        return [
            ExecutionAdapterResult(
                adapter_id=row["adapter_id"],
                action_id=row["action_id"],
                status=row["status"],
                message=row["message"],
            )
            for row in rows
        ]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
