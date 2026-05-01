from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.contracts.clarification_contract import Clarification


class ClarificationRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS clarifications (
                    clarification_id      TEXT PRIMARY KEY,
                    job_id                TEXT,
                    question              TEXT NOT NULL,
                    reason                TEXT NOT NULL,
                    status                TEXT NOT NULL DEFAULT 'pending',
                    blocking              INTEGER NOT NULL DEFAULT 1,
                    answer                TEXT,
                    traceable_origin_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_clarifications_job_id
                ON clarifications(job_id)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_clarifications_status
                ON clarifications(status)
                """
            )

    def save(self, clarification: Clarification) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO clarifications (
                    clarification_id, job_id, question, reason,
                    status, blocking, answer, traceable_origin_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(clarification_id) DO UPDATE SET
                    job_id                = excluded.job_id,
                    question              = excluded.question,
                    reason                = excluded.reason,
                    status                = excluded.status,
                    blocking              = excluded.blocking,
                    answer                = excluded.answer,
                    traceable_origin_json = excluded.traceable_origin_json
                """,
                (
                    clarification.clarification_id,
                    clarification.job_id,
                    clarification.question,
                    clarification.reason,
                    clarification.status,
                    int(clarification.blocking),
                    clarification.answer,
                    json.dumps(clarification.traceable_origin, ensure_ascii=False),
                ),
            )

    def save_batch(self, clarifications: list[Clarification]) -> None:
        for c in clarifications:
            self.save(c)

    def list_pending(self, job_id: str | None = None) -> list[Clarification]:
        query = """
            SELECT clarification_id, job_id, question, reason,
                   status, blocking, answer, traceable_origin_json
            FROM clarifications
            WHERE status = 'pending'
              AND (? IS NULL OR job_id = ?)
            ORDER BY clarification_id
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (job_id, job_id)).fetchall()
        return [_row_to_clarification(row) for row in rows]

    def mark_answered(self, clarification_id: str, answer: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE clarifications
                SET status = 'answered', answer = ?
                WHERE clarification_id = ?
                """,
                (answer, clarification_id),
            )

    def has_pending(self, job_id: str | None = None) -> bool:
        query = """
            SELECT COUNT(*) FROM clarifications
            WHERE status = 'pending'
              AND blocking = 1
              AND (? IS NULL OR job_id = ?)
        """
        with self._connect() as conn:
            count = conn.execute(query, (job_id, job_id)).fetchone()[0]
        return count > 0

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_clarification(row: sqlite3.Row) -> Clarification:
    return Clarification(
        clarification_id=row["clarification_id"],
        job_id=row["job_id"],
        question=row["question"],
        reason=row["reason"],
        status=row["status"],
        blocking=bool(row["blocking"]),
        answer=row["answer"],
        traceable_origin=json.loads(row["traceable_origin_json"]),
    )
