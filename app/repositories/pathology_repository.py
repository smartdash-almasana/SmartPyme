from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.contracts.pathology_contract import (
    PathologyFinding,
    PathologySeverity,
    PathologyStatus,
)


class PathologyRepository:
    def __init__(self, cliente_id: str, db_path: str | Path) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required for PathologyRepository")

        self.cliente_id = cliente_id
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pathology_findings (
                    cliente_id TEXT NOT NULL,
                    pathology_finding_id TEXT NOT NULL,
                    pathology_id TEXT NOT NULL,
                    formula_result_id TEXT NOT NULL,
                    formula_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    severity TEXT,
                    suggested_action TEXT,
                    source_refs_json TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (cliente_id, pathology_finding_id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_pathology_findings_cliente_pathology
                ON pathology_findings(cliente_id, pathology_id)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_pathology_findings_cliente_status
                ON pathology_findings(cliente_id, status)
                """
            )

    def save(self, pathology_finding_id: str, finding: PathologyFinding) -> None:
        if finding.cliente_id != self.cliente_id:
            raise ValueError("cliente_id mismatch")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO pathology_findings (
                    cliente_id,
                    pathology_finding_id,
                    pathology_id,
                    formula_result_id,
                    formula_id,
                    status,
                    severity,
                    suggested_action,
                    source_refs_json,
                    explanation,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cliente_id, pathology_finding_id) DO UPDATE SET
                    pathology_id = excluded.pathology_id,
                    formula_result_id = excluded.formula_result_id,
                    formula_id = excluded.formula_id,
                    status = excluded.status,
                    severity = excluded.severity,
                    suggested_action = excluded.suggested_action,
                    source_refs_json = excluded.source_refs_json,
                    explanation = excluded.explanation,
                    metadata_json = excluded.metadata_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    self.cliente_id,
                    pathology_finding_id,
                    finding.pathology_id,
                    finding.formula_result_id,
                    finding.formula_id,
                    finding.status.value,
                    finding.severity.value if finding.severity else None,
                    finding.suggested_action,
                    json.dumps(finding.source_refs, ensure_ascii=False),
                    finding.explanation,
                    json.dumps(finding.metadata, ensure_ascii=False),
                ),
            )

    def get(self, pathology_finding_id: str) -> PathologyFinding | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT * FROM pathology_findings
                WHERE cliente_id = ? AND pathology_finding_id = ?
                """,
                (self.cliente_id, pathology_finding_id),
            ).fetchone()

        if row is None:
            return None
        return _row_to_pathology_finding(row)

    def list_findings(
        self,
        pathology_id: str | None = None,
        status: PathologyStatus | str | None = None,
    ) -> list[PathologyFinding]:
        status_value = status.value if isinstance(status, PathologyStatus) else status
        query = """
            SELECT * FROM pathology_findings
            WHERE cliente_id = ?
              AND (? IS NULL OR pathology_id = ?)
              AND (? IS NULL OR status = ?)
            ORDER BY created_at DESC
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                query,
                (self.cliente_id, pathology_id, pathology_id, status_value, status_value),
            ).fetchall()
        return [_row_to_pathology_finding(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_pathology_finding(row: sqlite3.Row) -> PathologyFinding:
    severity = row["severity"]
    return PathologyFinding(
        cliente_id=row["cliente_id"],
        pathology_id=row["pathology_id"],
        formula_result_id=row["formula_result_id"],
        formula_id=row["formula_id"],
        status=PathologyStatus(row["status"]),
        severity=PathologySeverity(severity) if severity else None,
        suggested_action=row["suggested_action"],
        source_refs=json.loads(row["source_refs_json"]),
        explanation=row["explanation"],
        metadata=json.loads(row["metadata_json"]),
    )
