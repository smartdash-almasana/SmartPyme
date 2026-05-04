import pytest

from app.contracts.diagnostic_report import DiagnosticReport
from app.contracts.operational_case import OperationalCase
from app.services.diagnostic_service import DiagnosticService


def _case() -> OperationalCase:
    return OperationalCase(
        cliente_id="cli_123",
        case_id="case_456",
        job_id="job_789",
        skill_id="skill_001",
        hypothesis="Investigar si existe descuadre caja-banco",
        evidence_ids=["ev_1", "ev_2"],
    )


def test_generate_report_confirmed_with_evidence_and_findings():
    operational_case = _case()
    evidence_used = ["ev_1", "ev_2"]
    findings = [{"hallazgo": "descuadre de $1000", "cuenta": "caja"}]
    status = "CONFIRMED"

    report = DiagnosticService.generate_report(
        operational_case, evidence_used, findings, status
    )

    assert isinstance(report, DiagnosticReport)
    assert report.cliente_id == operational_case.cliente_id
    assert report.case_id == operational_case.case_id
    assert report.hypothesis == operational_case.hypothesis
    assert report.diagnosis_status == status
    assert report.evidence_used == evidence_used
    assert report.findings == findings
    assert report.report_id.startswith("dr_")
    assert len(report.report_id) == len("dr_") + 16


def test_generate_report_uses_deterministic_report_id_for_same_input():
    operational_case = _case()
    evidence_used = ["ev_1", "ev_2"]
    findings = [{"hallazgo": "descuadre de $1000", "cuenta": "caja"}]

    first_report = DiagnosticService.generate_report(
        operational_case, evidence_used, findings, "CONFIRMED"
    )
    second_report = DiagnosticService.generate_report(
        operational_case, evidence_used, findings, "CONFIRMED"
    )

    assert first_report.report_id == second_report.report_id


def test_generate_report_changes_report_id_when_evidence_changes():
    operational_case = _case()
    findings = [{"hallazgo": "descuadre de $1000", "cuenta": "caja"}]

    first_report = DiagnosticService.generate_report(
        operational_case, ["ev_1"], findings, "CONFIRMED"
    )
    second_report = DiagnosticService.generate_report(
        operational_case, ["ev_2"], findings, "CONFIRMED"
    )

    assert first_report.report_id != second_report.report_id


def test_generate_report_respects_manual_report_id():
    report = DiagnosticService.generate_report(
        _case(),
        ["ev_1"],
        [{"hallazgo": "algo"}],
        "CONFIRMED",
        report_id="dr_manual_001",
    )

    assert report.report_id == "dr_manual_001"


def test_generate_report_confirmed_without_evidence_raises():
    with pytest.raises(ValueError, match="requires non-empty evidence_used"):
        DiagnosticService.generate_report(
            _case(), [], [{"hallazgo": "algo"}], "CONFIRMED"
        )


def test_generate_report_confirmed_without_findings_raises():
    with pytest.raises(ValueError, match="requires non-empty findings"):
        DiagnosticService.generate_report(_case(), ["ev_1"], [], "CONFIRMED")


def test_generate_report_insufficient_evidence_allows_empty():
    operational_case = _case()

    report = DiagnosticService.generate_report(
        operational_case, [], [], "INSUFFICIENT_EVIDENCE"
    )

    assert report.diagnosis_status == "INSUFFICIENT_EVIDENCE"
    assert report.evidence_used == []
    assert report.findings == []
    assert report.cliente_id == operational_case.cliente_id
    assert report.case_id == operational_case.case_id


def test_generate_report_not_confirmed_allows_empty():
    report = DiagnosticService.generate_report(_case(), [], [], "NOT_CONFIRMED")

    assert report.diagnosis_status == "NOT_CONFIRMED"
    assert report.evidence_used == []
    assert report.findings == []


def test_generate_report_validates_tenant_id_not_present():
    report = DiagnosticService.generate_report(
        _case(), ["ev_1"], [{"hallazgo": "algo"}], "CONFIRMED"
    )

    dumped = report.model_dump()
    assert "tenant_id" not in dumped
    assert "tenant_id" not in dir(report)


def test_generate_report_preserves_non_empty_fields():
    operational_case = OperationalCase(
        cliente_id="cli_abc",
        case_id="case_def",
        job_id="job_ghi",
        skill_id="skill_jkl",
        hypothesis="¿Hay descuadre en caja?",
    )

    report = DiagnosticService.generate_report(
        operational_case, [], [], "INSUFFICIENT_EVIDENCE"
    )

    assert report.cliente_id == "cli_abc"
    assert report.case_id == "case_def"
    assert report.hypothesis == "¿Hay descuadre en caja?"
