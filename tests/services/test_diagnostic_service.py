import pytest

from app.contracts.diagnostic_report import DiagnosticReport
from app.contracts.operational_case import OperationalCase
from app.services.diagnostic_service import DiagnosticService


def test_generate_report_confirmed_with_evidence_and_findings():
    """Crea DiagnosticReport CONFIRMED con evidence y findings."""
    operational_case = OperationalCase(
        cliente_id="cli_123",
        case_id="case_456",
        job_id="job_789",
        skill_id="skill_001",
        hypothesis="Investigar si existe descuadre caja‑banco",
        evidence_ids=["ev_1", "ev_2"],
    )
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
    assert len(report.report_id) == len("dr_") + 12  # 12 caracteres hex


def test_generate_report_confirmed_without_evidence_raises():
    """Rechaza CONFIRMED si evidence_used está vacío."""
    operational_case = OperationalCase(
        cliente_id="cli_123",
        case_id="case_456",
        job_id="job_789",
        skill_id="skill_001",
        hypothesis="Investigar si existe descuadre",
    )
    evidence_used = []
    findings = [{"hallazgo": "algo"}]
    status = "CONFIRMED"

    with pytest.raises(ValueError, match="requires non‑empty evidence_used"):
        DiagnosticService.generate_report(
            operational_case, evidence_used, findings, status
        )


def test_generate_report_confirmed_without_findings_raises():
    """Rechaza CONFIRMED si findings está vacío."""
    operational_case = OperationalCase(
        cliente_id="cli_123",
        case_id="case_456",
        job_id="job_789",
        skill_id="skill_001",
        hypothesis="Investigar si existe descuadre",
    )
    evidence_used = ["ev_1"]
    findings = []
    status = "CONFIRMED"

    with pytest.raises(ValueError, match="requires non‑empty findings"):
        DiagnosticService.generate_report(
            operational_case, evidence_used, findings, status
        )


def test_generate_report_insufficient_evidence_allows_empty():
    """Permite evidence_used y findings vacíos cuando el estado es INSUFFICIENT_EVIDENCE."""
    operational_case = OperationalCase(
        cliente_id="cli_123",
        case_id="case_456",
        job_id="job_789",
        skill_id="skill_001",
        hypothesis="Investigar si existe descuadre",
    )
    evidence_used = []
    findings = []
    status = "INSUFFICIENT_EVIDENCE"

    report = DiagnosticService.generate_report(
        operational_case, evidence_used, findings, status
    )

    assert report.diagnosis_status == status
    assert report.evidence_used == []
    assert report.findings == []
    assert report.cliente_id == operational_case.cliente_id
    assert report.case_id == operational_case.case_id


def test_generate_report_not_confirmed_allows_empty():
    """Permite evidence_used y findings vacíos cuando el estado es NOT_CONFIRMED."""
    operational_case = OperationalCase(
        cliente_id="cli_123",
        case_id="case_456",
        job_id="job_789",
        skill_id="skill_001",
        hypothesis="Investigar si existe descuadre",
    )
    evidence_used = []
    findings = []
    status = "NOT_CONFIRMED"

    report = DiagnosticService.generate_report(
        operational_case, evidence_used, findings, status
    )

    assert report.diagnosis_status == status
    assert report.evidence_used == []
    assert report.findings == []


def test_generate_report_validates_tenant_id_not_present():
    """Verifica que el reporte no contenga tenant_id."""
    operational_case = OperationalCase(
        cliente_id="cli_123",
        case_id="case_456",
        job_id="job_789",
        skill_id="skill_001",
        hypothesis="Investigar si existe descuadre",
    )
    evidence_used = ["ev_1"]
    findings = [{"hallazgo": "algo"}]
    status = "CONFIRMED"

    report = DiagnosticService.generate_report(
        operational_case, evidence_used, findings, status
    )

    # DiagnosticReport no tiene tenant_id por diseño.
    # Asegurarnos de que el dict no contiene esa clave.
    dumped = report.model_dump()
    assert "tenant_id" not in dumped
    assert "tenant_id" not in dir(report)


def test_generate_report_preserves_non_empty_fields():
    """Preserva cliente_id, case_id, hypothesis aunque evidence_used/findings estén vacíos."""
    operational_case = OperationalCase(
        cliente_id="cli_abc",
        case_id="case_def",
        job_id="job_ghi",
        skill_id="skill_jkl",
        hypothesis="¿Hay descuadre en caja?",
    )
    evidence_used = []
    findings = []
    status = "INSUFFICIENT_EVIDENCE"

    report = DiagnosticService.generate_report(
        operational_case, evidence_used, findings, status
    )

    assert report.cliente_id == "cli_abc"
    assert report.case_id == "case_def"
    assert report.hypothesis == "¿Hay descuadre en caja?"