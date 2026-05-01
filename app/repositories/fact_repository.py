from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from app.contracts.evidence_contract import ExtractedFactCandidate


def _default_db_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "facts.db"


def _get_db_path() -> Path:
    raw_path = os.getenv("SMARTPYME_FACTS_DB")
    return Path(raw_path) if raw_path else _default_db_path()


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def _ensure_cliente_id_column(conn: sqlite3.Connection) -> None:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(extracted_facts)").fetchall()}
    if "cliente_id" not in columns:
        conn.execute(
            "ALTER TABLE extracted_facts "
            "ADD COLUMN cliente_id TEXT NOT NULL DEFAULT '__migration_pending__'"
        )


def init_facts_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS extracted_facts (
                cliente_id TEXT NOT NULL,
                fact_candidate_id TEXT PRIMARY KEY,
                evidence_id TEXT NOT NULL,
                job_id TEXT,
                plan_id TEXT,
                schema_name TEXT NOT NULL,
                fact_type TEXT,
                data_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                extraction_method TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                errors_json TEXT NOT NULL
            )
            """
        )
        _ensure_cliente_id_column(conn)
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_extracted_facts_cliente_id
            ON extracted_facts(cliente_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_extracted_facts_evidence_id
            ON extracted_facts(evidence_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_extracted_facts_fact_type
            ON extracted_facts(fact_type)
            """
        )


class FactRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else _get_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self) -> None:
        previous_env = os.environ.get("SMARTPYME_FACTS_DB")
        os.environ["SMARTPYME_FACTS_DB"] = str(self.db_path)
        try:
            init_facts_db()
        finally:
            if previous_env is None:
                os.environ.pop("SMARTPYME_FACTS_DB", None)
            else:
                os.environ["SMARTPYME_FACTS_DB"] = previous_env

    def save(self, fact: ExtractedFactCandidate) -> None:
        data_json = json.dumps(fact.data, ensure_ascii=False, sort_keys=True)
        errors_json = json.dumps(fact.errors, ensure_ascii=False)
        fact_type = fact.data.get("fact_type")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO extracted_facts (
                    cliente_id,
                    fact_candidate_id,
                    evidence_id,
                    job_id,
                    plan_id,
                    schema_name,
                    fact_type,
                    data_json,
                    confidence,
                    extraction_method,
                    validation_status,
                    errors_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(fact_candidate_id) DO UPDATE SET
                    cliente_id = excluded.cliente_id,
                    evidence_id = excluded.evidence_id,
                    job_id = excluded.job_id,
                    plan_id = excluded.plan_id,
                    schema_name = excluded.schema_name,
                    fact_type = excluded.fact_type,
                    data_json = excluded.data_json,
                    confidence = excluded.confidence,
                    extraction_method = excluded.extraction_method,
                    validation_status = excluded.validation_status,
                    errors_json = excluded.errors_json
                """,
                (
                    fact.cliente_id,
                    fact.fact_candidate_id,
                    fact.evidence_id,
                    fact.job_id,
                    fact.plan_id,
                    fact.schema_name,
                    fact_type,
                    data_json,
                    fact.confidence,
                    fact.extraction_method,
                    fact.validation_status,
                    errors_json,
                ),
            )

    def save_batch(self, facts: list[ExtractedFactCandidate]) -> None:
        for fact in facts:
            self.save(fact)

    def list_facts(
        self,
        *,
        evidence_id: str | None = None,
        fact_type: str | None = None,
    ) -> list[ExtractedFactCandidate]:
        query = """
            SELECT
                cliente_id,
                fact_candidate_id,
                evidence_id,
                job_id,
                plan_id,
                schema_name,
                data_json,
                confidence,
                extraction_method,
                validation_status,
                errors_json
            FROM extracted_facts
            WHERE (? IS NULL OR evidence_id = ?)
              AND (? IS NULL OR fact_type = ?)
            ORDER BY fact_candidate_id
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                query,
                (evidence_id, evidence_id, fact_type, fact_type),
            ).fetchall()
        return [_row_to_fact(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_fact(row: sqlite3.Row) -> ExtractedFactCandidate:
    return ExtractedFactCandidate(
        cliente_id=row["cliente_id"],
        fact_candidate_id=row["fact_candidate_id"],
        evidence_id=row["evidence_id"],
        job_id=row["job_id"],
        plan_id=row["plan_id"],
        schema_name=row["schema_name"],
        data=json.loads(row["data_json"]),
        confidence=float(row["confidence"]),
        extraction_method=row["extraction_method"],
        validation_status=row["validation_status"],
        errors=json.loads(row["errors_json"]),
    )
