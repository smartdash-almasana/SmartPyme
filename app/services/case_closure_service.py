import uuid
from datetime import datetime
from dataclasses import asdict
from app.repositories.operational_case_repository import OperationalCaseRepository
from app.contracts.operational_case_contract import ValidatedCaseRecord, QuantifiedImpact

class CaseClosureService:
    def __init__(self, repo: OperationalCaseRepository):
        self.repo = repo

    def close_case(self, case_id: str, report_id: str | None = None) -> str | None:
        case = self.repo.get_case(case_id)
        if not case:
            return None
        
        report = self.repo.get_report(report_id) if report_id else self.repo.get_diagnostic_report_by_case(case_id)
        
        if not report or report.cliente_id != self.repo.cliente_id or not report.findings:
            return None

        # Construir record
        record = ValidatedCaseRecord(
            validated_case_id=str(uuid.uuid4()),
            cliente_id=case.cliente_id,
            job_id=case.job_id,
            case_id=case.case_id,
            report_id=report.report_id,
            timestamp=datetime.utcnow().isoformat(),
            payload={
                "hypothesis": report.hypothesis,
                "evidence_used": report.evidence_used,
                "formulas_used": report.formulas_used,
                "findings_summary": report.reasoning_summary,
                "quantified_impact": asdict(report.quantified_impact),
                "owner_visible_report": f"Caso cerrado con diagnóstico {report.diagnosis_status}.",
                "next_question": report.owner_question
            },
            diagnosis_status=report.diagnosis_status,
            audit_id=str(uuid.uuid4()),
            audit_created_at=datetime.utcnow().isoformat(),
            formulas_used=report.formulas_used,
            findings_summary=report.reasoning_summary,
            quantified_impact=report.quantified_impact
        )

        self.repo.create_validated_case(record)
        self.repo.update_case_status(case_id, "CLOSED")

        return record.validated_case_id
