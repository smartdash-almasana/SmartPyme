from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.services.findings_service import Finding


class FindingRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS findings (
                    finding_id          TEXT PRIMARY KEY,
                    entity_id_a         TEXT NOT NULL,
                    entity_id_b         TEXT NOT NULL,
                    entity_type         TEXT NOT NULL,
                    metric              TEXT NOT NULL,
                    source_a_value      TEXT NOT NULL,
                    source_b_value      TEXT NOT NULL,
                    difference          REAL NOT NULL,
                    difference_pct      REAL NOT NULL,
                    severity            TEXT NOT NULL,
                    suggested_action    TEXT NOT NULL,
                    traceable_origin_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_findings_entity_type
                ON findings(entity_type)
                """
            )

    def save(self, finding: Finding) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO findings (
                    finding_id, entity_id_a, entity_id_b, entity_type,
                    metric, source_a_value, source_b_value,
                    difference, difference_pct, severity,
                    suggested_action, traceable_origin_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(finding_id) DO UPDATE SET
                    entity_id_a         = excluded.entity_id_a,
                    entity_id_b         = excluded.entity_id_b,
                    entity_type         = excluded.entity_type,
                    metric              = excluded.metric,
                    source_a_value      = excluded.source_a_value,
                    source_b_value      = excluded.source_b_value,
                    difference          = excluded.difference,
                    difference_pct      = excluded.difference_pct,
                    severity            = excluded.severity,
                    suggested_action    = excluded.suggested_action,
                    traceable_origin_json = excluded.traceable_origin_json
                """,
                (
                    finding.finding_id,
                    finding.entity_id_a,
                    finding.entity_id_b,
                    finding.entity_type,
                    finding.metric,
                    json.dumps(finding.source_a_value),
                    json.dumps(finding.source_b_value),
                    finding.difference,
                    finding.difference_pct,
                    finding.severity,
                    finding.suggested_action,
                    json.dumps(finding.traceable_origin, ensure_ascii=False),
                ),
            )

    def save_batch(self, findings: list[Finding]) -> None:
        for finding in findings:
            self.save(finding)

    def list_findings(self, entity_type: str | None = None) -> list[Finding]:
        query = """
            SELECT
                finding_id, entity_id_a, entity_id_b, entity_type,
                metric, source_a_value, source_b_value,
                difference, difference_pct, severity,
                suggested_action, traceable_origin_json
            FROM findings
            WHERE (? IS NULL OR entity_type = ?)
            ORDER BY finding_id
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (entity_type, entity_type)).fetchall()
        return [_row_to_finding(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_finding(row: sqlite3.Row) -> Finding:
    return Finding(
        finding_id=row["finding_id"],
        entity_id_a=row["entity_id_a"],
        entity_id_b=row["entity_id_b"],
        entity_type=row["entity_type"],
        metric=row["metric"],
        source_a_value=json.loads(row["source_a_value"]),
        source_b_value=json.loads(row["source_b_value"]),
        difference=row["difference"],
        difference_pct=row["difference_pct"],
        severity=row["severity"],
        suggested_action=row["suggested_action"],
        traceable_origin=json.loads(row["traceable_origin_json"]),
    )
