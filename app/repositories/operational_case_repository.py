from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any, TypeVar, Type, cast

from app.contracts.operational_case_contract import (
    OperationalCase,
    DiagnosticReport,
    ValidatedCaseRecord,
    FindingRecord,
    QuantifiedImpact,
)

T = TypeVar("T")


class OperationalCaseRepository:
    def __init__(self, cliente_id: str, db_path: str | Path):
        self.cliente_id = cliente_id
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS operational_cases (
                    cliente_id TEXT,
                    case_id TEXT,
                    job_id TEXT,
                    skill_id TEXT,
                    payload TEXT,
                    status TEXT,
                    PRIMARY KEY (cliente_id, case_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS diagnostic_reports (
                    cliente_id TEXT,
                    report_id TEXT,
                    case_id TEXT,
                    job_id TEXT,
                    payload TEXT,
                    diagnosis_status TEXT,
                    PRIMARY KEY (cliente_id, report_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS validated_case_records (
                    cliente_id TEXT,
                    validated_case_id TEXT,
                    job_id TEXT,
                    case_id TEXT,
                    report_id TEXT,
                    timestamp TEXT,
                    payload TEXT,
                    diagnosis_status TEXT,
                    PRIMARY KEY (cliente_id, validated_case_id)
                )
                """
            )

    def _verify_isolation(self, entity_cliente_id: str):
        if entity_cliente_id != self.cliente_id:
            raise ValueError(
                f"Violación de aislamiento multi-tenant: {entity_cliente_id} != {self.cliente_id}"
            )

    # --- OperationalCase ---

    def create_case(self, case: OperationalCase) -> None:
        self._verify_isolation(case.cliente_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO operational_cases (cliente_id, case_id, job_id, skill_id, payload, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    case.cliente_id,
                    case.case_id,
                    case.job_id,
                    case.skill_id,
                    json.dumps(asdict(case), ensure_ascii=False),
                    case.status,
                ),
            )

    def get_case(self, case_id: str) -> OperationalCase | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT payload FROM operational_cases WHERE cliente_id = ? AND case_id = ?",
                (self.cliente_id, case_id),
            )
            row = cursor.fetchone()
            if row:
                data = json.loads(row["payload"])
                return OperationalCase(**data)
        return None

    def update_case_status(self, case_id: str, new_status: str) -> bool:
        if new_status not in ["OPEN", "IN_PROGRESS", "CLOSED"]:
            return False
        with sqlite3.connect(self.db_path) as conn:
            # We must fetch first to ensure isolation check via get_case or verify here
            case = self.get_case(case_id)
            if not case:
                return False
            
            # Re-verify isolation explicitly as safety measure
            self._verify_isolation(case.cliente_id)
            
            # Update payload to reflect new status
            updated_payload = asdict(case)
            updated_payload["status"] = new_status
            
            conn.execute(
                "UPDATE operational_cases SET status = ?, payload = ? WHERE cliente_id = ? AND case_id = ?",
                (new_status, json.dumps(updated_payload, ensure_ascii=False), self.cliente_id, case_id),
            )
            return conn.total_changes > 0

    def list_cases(self) -> list[OperationalCase]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT payload FROM operational_cases WHERE cliente_id = ?",
                (self.cliente_id,),
            )
            return [OperationalCase(**json.loads(row["payload"])) for row in cursor.fetchall()]

    def create_report(self, report: DiagnosticReport) -> None:
        self._verify_isolation(report.cliente_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO diagnostic_reports (cliente_id, report_id, case_id, job_id, payload, diagnosis_status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report.cliente_id,
                    report.report_id,
                    report.case_id,
                    report.job_id,
                    json.dumps(asdict(report), ensure_ascii=False),
                    report.diagnosis_status,
                ),
            )

    def get_report(self, report_id: str) -> DiagnosticReport | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT payload FROM diagnostic_reports WHERE cliente_id = ? AND report_id = ?",
                (self.cliente_id, report_id),
            )
            row = cursor.fetchone()
            if row:
                data = json.loads(row["payload"])
                return self._inflate_report(data)
        return None

    def list_reports(self) -> list[DiagnosticReport]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT payload FROM diagnostic_reports WHERE cliente_id = ?",
                (self.cliente_id,),
            )
            return [self._inflate_report(json.loads(row["payload"])) for row in cursor.fetchall()]

    def _inflate_report(self, data: dict[str, Any]) -> DiagnosticReport:
        # Pydantic would handle this automatically, but with pure dataclasses we need to inflate nested objects
        findings = [FindingRecord(**f) for f in data.pop("findings", [])]
        impact_data = data.pop("quantified_impact")
        impact = QuantifiedImpact(**impact_data)
        references_used = data.pop("references_used", [])
        return DiagnosticReport(findings=findings, quantified_impact=impact, references_used=references_used, **data)

    # --- ValidatedCaseRecord ---

    def create_validated_case(self, record: ValidatedCaseRecord) -> None:
        self._verify_isolation(record.cliente_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO validated_case_records (
                    cliente_id, validated_case_id, job_id, case_id, report_id, timestamp, payload, diagnosis_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.cliente_id,
                    record.validated_case_id,
                    record.job_id,
                    record.case_id,
                    record.report_id,
                    record.timestamp,
                    json.dumps(asdict(record), ensure_ascii=False),
                    record.diagnosis_status,
                ),
            )

    def get_validated_case(self, validated_case_id: str) -> ValidatedCaseRecord | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT payload FROM validated_case_records WHERE cliente_id = ? AND validated_case_id = ?",
                (self.cliente_id, validated_case_id),
            )
            row = cursor.fetchone()
            if row:
                data = json.loads(row["payload"])
                return self._inflate_validated_case(data)
        return None

    def list_validated_cases(self) -> list[ValidatedCaseRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT payload FROM validated_case_records WHERE cliente_id = ?",
                (self.cliente_id,),
            )
            return [
                self._inflate_validated_case(json.loads(row["payload"]))
                for row in cursor.fetchall()
            ]

    def _inflate_validated_case(self, data: dict[str, Any]) -> ValidatedCaseRecord:
        impact_data = data.pop("quantified_impact")
        impact = QuantifiedImpact(**impact_data)
        return ValidatedCaseRecord(quantified_impact=impact, **data)
