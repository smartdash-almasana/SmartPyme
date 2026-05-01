from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from app.contracts.evidence_contract import CanonicalRowCandidate


def _default_db_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "canonical.db"


def _get_db_path() -> Path:
    raw_path = os.getenv("SMARTPYME_CANONICAL_DB")
    return Path(raw_path) if raw_path else _default_db_path()


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_canonical_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS canonical_rows (
                cliente_id TEXT NOT NULL,
                canonical_row_id TEXT NOT NULL,
                fact_candidate_id TEXT NOT NULL,
                evidence_id TEXT NOT NULL,
                job_id TEXT,
                plan_id TEXT,
                entity_type TEXT NOT NULL,
                row_json TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                errors_json TEXT NOT NULL,
                PRIMARY KEY (cliente_id, canonical_row_id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_canonical_rows_cliente_id
            ON canonical_rows(cliente_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_canonical_rows_cliente_id_evidence_id
            ON canonical_rows(cliente_id, evidence_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_canonical_rows_cliente_id_entity_type
            ON canonical_rows(cliente_id, entity_type)
            """
        )


class CanonicalRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else _get_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self) -> None:
        previous_env = os.environ.get("SMARTPYME_CANONICAL_DB")
        os.environ["SMARTPYME_CANONICAL_DB"] = str(self.db_path)
        try:
            init_canonical_db()
        finally:
            if previous_env is None:
                os.environ.pop("SMARTPYME_CANONICAL_DB", None)
            else:
                os.environ["SMARTPYME_CANONICAL_DB"] = previous_env

    def save(self, canonical_row: CanonicalRowCandidate) -> None:
        row_json = json.dumps(canonical_row.row, ensure_ascii=False, sort_keys=True)
        errors_json = json.dumps(canonical_row.errors, ensure_ascii=False)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO canonical_rows (
                    cliente_id,
                    canonical_row_id,
                    fact_candidate_id,
                    evidence_id,
                    job_id,
                    plan_id,
                    entity_type,
                    row_json,
                    validation_status,
                    errors_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cliente_id, canonical_row_id) DO UPDATE SET
                    fact_candidate_id = excluded.fact_candidate_id,
                    evidence_id = excluded.evidence_id,
                    job_id = excluded.job_id,
                    plan_id = excluded.plan_id,
                    entity_type = excluded.entity_type,
                    row_json = excluded.row_json,
                    validation_status = excluded.validation_status,
                    errors_json = excluded.errors_json
                """,
                (
                    canonical_row.cliente_id,
                    canonical_row.canonical_row_id,
                    canonical_row.fact_candidate_id,
                    canonical_row.evidence_id,
                    canonical_row.job_id,
                    canonical_row.plan_id,
                    canonical_row.entity_type,
                    row_json,
                    canonical_row.validation_status,
                    errors_json,
                ),
            )

    def save_batch(self, canonical_rows: list[CanonicalRowCandidate]) -> None:
        for row in canonical_rows:
            self.save(row)

    def list_canonical_rows(
        self,
        *,
        cliente_id: str | None = None,
        evidence_id: str | None = None,
        entity_type: str | None = None,
    ) -> list[CanonicalRowCandidate]:
        query = """
            SELECT
                cliente_id,
                canonical_row_id,
                fact_candidate_id,
                evidence_id,
                job_id,
                plan_id,
                entity_type,
                row_json,
                validation_status,
                errors_json
            FROM canonical_rows
            WHERE (? IS NULL OR cliente_id = ?)
              AND (? IS NULL OR evidence_id = ?)
              AND (? IS NULL OR entity_type = ?)
            ORDER BY canonical_row_id
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                query,
                (cliente_id, cliente_id, evidence_id, evidence_id, entity_type, entity_type),
            ).fetchall()
        return [_row_to_canonical_row(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_canonical_row(row: sqlite3.Row) -> CanonicalRowCandidate:
    return CanonicalRowCandidate(
        cliente_id=row["cliente_id"],
        canonical_row_id=row["canonical_row_id"],
        fact_candidate_id=row["fact_candidate_id"],
        evidence_id=row["evidence_id"],
        job_id=row["job_id"],
        plan_id=row["plan_id"],
        entity_type=row["entity_type"],
        row=json.loads(row["row_json"]),
        validation_status=row["validation_status"],
        errors=json.loads(row["errors_json"]),
    )
