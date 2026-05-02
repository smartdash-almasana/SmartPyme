import pytest
from app.contracts.operational_case_contract import DiagnosticReport, FindingRecord, QuantifiedImpact

def test_diagnostic_report_confirmation_requires_findings():
    impact = QuantifiedImpact(amount=100.0, currency="USD")
    with pytest.raises(ValueError, match="FINDINGS_REQUERIDOS"):
        DiagnosticReport(
            report_id="r1", case_id="c1", cliente_id="cli1", job_id="j1",
            hypothesis="Investigar si A?", diagnosis_status="CONFIRMED",
            findings=[], evidence_used=[], formulas_used=[],
            quantified_impact=impact, reasoning_summary="...",
            proposed_next_actions=["..."], owner_question="..."
        )

def test_diagnostic_report_success():
    impact = QuantifiedImpact(amount=100.0, currency="USD")
    finding = FindingRecord(
        entity="e1", finding_type="t1", measured_difference={"diff": 10},
        compared_sources=["s1"], evidence_used=["ev1"], severity="LOW", recommendation="rec"
    )
    report = DiagnosticReport(
        report_id="r1", case_id="c1", cliente_id="cli1", job_id="j1",
        hypothesis="Investigar si A?", diagnosis_status="CONFIRMED",
        findings=[finding], evidence_used=["ev1"], formulas_used=["f1"],
        quantified_impact=impact, reasoning_summary="...",
        proposed_next_actions=["..."], owner_question="..."
    )
    assert report.report_id == "r1"
    assert len(report.findings) == 1
