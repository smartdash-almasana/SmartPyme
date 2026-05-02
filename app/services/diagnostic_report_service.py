import uuid
from typing import List
from app.contracts.operational_case_contract import DiagnosticReport, FindingRecord, QuantifiedImpact

class DiagnosticReportService:
    def create_report(self, case_id: str, cliente_id: str, job_id: str, hypothesis: str, findings: List[FindingRecord], evidence_used: List[str], formulas_used: List[str], quantified_impact: QuantifiedImpact, reasoning_summary: str, references_used: List[str] = None) -> DiagnosticReport:
        
        diagnosis_status = "CONFIRMED"
        
        # Validaciones de Invalidez
        if not evidence_used:
            diagnosis_status = "INSUFFICIENT_EVIDENCE"
        
        for finding in findings:
            if not finding.compared_sources:
                diagnosis_status = "INSUFFICIENT_EVIDENCE"
                break
            if not finding.measured_difference:
                diagnosis_status = "INSUFFICIENT_EVIDENCE"
                break
                
        # Validación extra: si es CONFIRMED, debe tener al menos un hallazgo y evidencia
        if diagnosis_status == "CONFIRMED":
            if not findings or not evidence_used:
                diagnosis_status = "INSUFFICIENT_EVIDENCE"

        return DiagnosticReport(
            report_id=str(uuid.uuid4()),
            case_id=case_id,
            cliente_id=cliente_id,
            job_id=job_id,
            hypothesis=hypothesis,
            diagnosis_status=diagnosis_status,
            findings=findings,
            evidence_used=evidence_used,
            formulas_used=formulas_used,
            quantified_impact=quantified_impact,
            reasoning_summary=reasoning_summary,
            proposed_next_actions=["Revisar hallazgos", "Autorizar acciones correctivas"],
            owner_question="¿Desea autorizar la implementación de acciones correctivas?",
            references_used=references_used or []
        )
