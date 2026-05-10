from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.contracts.bem_runs import BemRunRecord


class BemRunRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def create(self, run: BemRunRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO bem_runs (
                    tenant_id,
                    run_id,
                    workflow_id,
                    status,
                    request_payload_json,
                    response_payload_json,
                    created_at,
                    updated_at,
                    error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.tenant_id,
                    run.run_id,
                    run.workflow_id,
                    run.status,
                    json.dumps(run.request_payload, ensure_ascii=False),
                    json.dumps(run.response_payload, ensure_ascii=False)
                    if run.response_payload is not None
                    else None,
                    run.created_at,
                    run.updated_at,
                    run.error_message,
                ),
            )

    def mark_completed(
        self,
        tenant_id: str,
        run_id: str,
        response_payload: dict[str, Any],
        updated_at: str,
    ) -> None:
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(run_id, "run_id")
        _require_non_empty(updated_at, "updated_at")
        if not isinstance(response_payload, dict) or not response_payload:
            raise ValueError("response_payload is required")

        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE bem_runs
                SET status = ?, response_payload_json = ?, updated_at = ?, error_message = NULL
                WHERE tenant_id = ? AND run_id = ?
                """,
                (
                    "COMPLETED",
                    json.dumps(response_payload, ensure_ascii=False),
                    updated_at,
                    tenant_id.strip(),
                    run_id.strip(),
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError("run not found")

    def mark_failed(
        self,
        tenant_id: str,
        run_id: str,
        error_message: str,
        updated_at: str,
    ) -> None:
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(run_id, "run_id")
        _require_non_empty(error_message, "error_message")
        _require_non_empty(updated_at, "updated_at")

        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE bem_runs
                SET status = ?, updated_at = ?, error_message = ?
                WHERE tenant_id = ? AND run_id = ?
                """,
                ("FAILED", updated_at, error_message.strip(), tenant_id.strip(), run_id.strip()),
            )
            if cursor.rowcount != 1:
                raise ValueError("run not found")

    def get_by_run_id(self, tenant_id: str, run_id: str) -> BemRunRecord | None:
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(run_id, "run_id")

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT * FROM bem_runs
                WHERE tenant_id = ? AND run_id = ?
                """,
                (tenant_id.strip(), run_id.strip()),
            ).fetchone()
        if row is None:
            return None
        return _row_to_bem_run(row)

    def list_by_tenant(self, tenant_id: str) -> list[BemRunRecord]:
        _require_non_empty(tenant_id, "tenant_id")
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM bem_runs
                WHERE tenant_id = ?
                ORDER BY created_at DESC
                """,
                (tenant_id.strip(),),
            ).fetchall()
        return [_row_to_bem_run(row) for row in rows]

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bem_runs (
                    tenant_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request_payload_json TEXT NOT NULL,
                    response_payload_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    error_message TEXT,
                    PRIMARY KEY (tenant_id, run_id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_bem_runs_tenant_created_at
                ON bem_runs(tenant_id, created_at)
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _row_to_bem_run(row: sqlite3.Row) -> BemRunRecord:
    response_raw = row["response_payload_json"]
    return BemRunRecord(
        tenant_id=row["tenant_id"],
        run_id=row["run_id"],
        workflow_id=row["workflow_id"],
        status=row["status"],
        request_payload=json.loads(row["request_payload_json"]),
        response_payload=json.loads(response_raw) if response_raw else None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        error_message=row["error_message"],
    )
