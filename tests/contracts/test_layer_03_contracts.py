import pytest

from app.contracts.action_proposal import ActionProposal
from app.contracts.diagnostic_report import DiagnosticReport
from app.contracts.operational_case import OperationalCase


def test_create_valid_operational_case() -> None:
    case = OperationalCase(
        cliente_id="cliente_1",
        case_id="case_1",
        job_id="job_1",
        skill_id="skill_margin_leak_audit",
        hypothesis="Investigar si existe pérdida de margen.",
        evidence_ids=["evidence_1"],
        status="READY_FOR_INVESTIGATION",
    )

    assert case.model_dump()["cliente_id"] == "cliente_1"
    assert case.model_dump()["status"] == "READY_FOR_INVESTIGATION"


@pytest.mark.parametrize(
    "hypothesis",
    [
        "Investigar si existe pérdida de margen.",
        "Analizar si existe descuadre entre caja y banco.",
        "¿Existe pérdida de stock en el período revisado?",
    ],
)
def test_operational_case_accepts_investigable_hypothesis(hypothesis: str) -> None:
    case = OperationalCase(
        cliente_id="cliente_1",
        case_id="case_1",
        job_id="job_1",
        skill_id="skill_margin_leak_audit",
        hypothesis=hypothesis,
    )

    assert case.model_dump()["hypothesis"] == hypothesis


def test_operational_case_rejects_affirmative_non_investigable_hypothesis() -> None:
    with pytest.raises(ValueError, match="HYPOTHESIS_INVALIDA"):
        OperationalCase(
            cliente_id="cliente_1",
            case_id="case_1",
            job_id="job_1",
            skill_id="skill_margin_leak_audit",
            hypothesis="Hay pérdida de margen.",
        )


@pytest.mark.parametrize(
    "diagnosis_status",
    ["CONFIRMED", "NOT_CONFIRMED", "INSUFFICIENT_EVIDENCE"],
)
def test_create_diagnostic_report_with_allowed_statuses(diagnosis_status: str) -> None:
    report = DiagnosticReport(
        cliente_id="cliente_1",
        report_id="report_1",
        case_id="case_1",
        hypothesis="Investigar si existe pérdida de margen.",
        diagnosis_status=diagnosis_status,
        findings=[],
        evidence_used=["evidence_1"],
        reasoning_summary="Reporte mínimo de investigación.",
    )

    assert report.model_dump()["diagnosis_status"] == diagnosis_status


def test_reject_invalid_diagnosis_status() -> None:
    with pytest.raises(ValueError, match="invalid diagnosis_status"):
        DiagnosticReport(
            cliente_id="cliente_1",
            report_id="report_1",
            case_id="case_1",
            hypothesis="Investigar si existe pérdida de margen.",
            diagnosis_status="EXECUTE",
            reasoning_summary="Reporte mínimo de investigación.",
        )


def test_create_valid_action_proposal() -> None:
    proposal = ActionProposal(
        cliente_id="cliente_1",
        proposal_id="proposal_1",
        report_id="report_1",
        recommended_action="Preparar plan de corrección de precios.",
        rationale="El reporte requiere una propuesta posterior para decisión del dueño.",
    )

    assert proposal.model_dump()["requires_owner_decision"] is True


def test_reject_action_proposal_without_owner_decision() -> None:
    with pytest.raises(ValueError, match="requires owner decision"):
        ActionProposal(
            cliente_id="cliente_1",
            proposal_id="proposal_1",
            report_id="report_1",
            recommended_action="Ejecutar corrección automática.",
            rationale="No debe autorizarse desde la propuesta.",
            requires_owner_decision=False,
        )
