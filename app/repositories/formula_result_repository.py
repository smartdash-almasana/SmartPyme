from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.contracts.formula_contract import FormulaResult, FormulaStatus


class FormulaResultRepository:
    def __init__(self, cliente_id: str, db_path: str | Path) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required for FormulaResultRepository")

        self.cliente_id = cliente_id
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS formula_results (
                    cliente_id TEXT NOT NULL,
                    result_id TEXT NOT NULL,
                    formula_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    value REAL,
                    inputs_json TEXT NOT NULL,
                    source_refs_json TEXT NOT NULL,
                    blocking_reason TEXT,
                    metadata_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (cliente_id, result_id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_formula_results_cliente_formula
                ON formula_results(cliente_id, formula_id)
                """
            )

    def save(self, result_id: str, result: FormulaResult) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO formula_results (
                    cliente_id, result_id, formula_id, status, value,
                    inputs_json, source_refs_json, blocking_reason, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cliente_id, result_id) DO UPDATE SET
                    formula_id = excluded.formula_id,
                    status = excluded.status,
                    value = excluded.value,
                    inputs_json = excluded.inputs_json,
                    source_refs_json = excluded.source_refs_json,
                    blocking_reason = excluded.blocking_reason,
                    metadata_json = excluded.metadata_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    self.cliente_id,
                    result_id,
                    result.formula_id,
                    result.status.value,
                    result.value,
                    json.dumps(result.inputs, ensure_ascii=False),
                    json.dumps(result.source_refs, ensure_ascii=False),
                    result.blocking_reason,
                    json.dumps(result.metadata, ensure_ascii=False),
                ),
            )

    def get(self, result_id: str) -> FormulaResult | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM formula_results WHERE cliente_id = ? AND result_id = ?",
                (self.cliente_id, result_id),
            ).fetchone()

        if row is None:
            return None
        return _row_to_formula_result(row)

    def list_results(self, formula_id: str | None = None) -> list[FormulaResult]:
        query = """
            SELECT * FROM formula_results
            WHERE cliente_id = ?
              AND (? IS NULL OR formula_id = ?)
            ORDER BY created_at DESC
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (self.cliente_id, formula_id, formula_id)).fetchall()
        return [_row_to_formula_result(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_formula_result(row: sqlite3.Row) -> FormulaResult:
    return FormulaResult(
        formula_id=row["formula_id"],
        status=FormulaStatus(row["status"]),
        value=row["value"],
        inputs=json.loads(row["inputs_json"]),
        source_refs=json.loads(row["source_refs_json"]),
        blocking_reason=row["blocking_reason"],
        metadata=json.loads(row["metadata_json"]),
    )
