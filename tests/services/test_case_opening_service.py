"""
Tests — CaseOpeningService — Capa 03
TS_030_002_SERVICIO_APERTURA_CASO
"""

import uuid

import pytest

from app.contracts.investigation_contract import (
    AvailableVariableMatch,
    EvidenceGap,
    OperationalCaseCandidate,
)
from app.contracts.operational_case_v2_contract import OperationalCase
from app.services.case_opening_service import CaseOpeningService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _match() -> AvailableVariableMatch:
    return AvailableVariableMatch(
        match_id="m1",
        required_variable_id="var_stock",
        clean_variable_id="cv_stock",
        evidence_ref_id="ref_excel",
        confidence=0.82,
    )


def _gap_critical_no_src() -> EvidenceGap:
    return EvidenceGap(
        gap_id="g_crit",
        required_variable_id="var_costo",
        variable_canonical_name="costo_unitario",
        reason="No encontrado.",
        impact="No se puede calcular capital.",
        required_source=None,
        priority="CRITICAL",
    )


def _gap_high_with_src() -> EvidenceGap:
    return EvidenceGap(
        gap_id="g_high",
        required_variable_id="var_precio",
        variable_canonical_name="precio_venta",
        reason="No en Excel.",
        impact="No se puede calcular margen.",
        required_source="Lista de precios del proveedor.",
        priority="HIGH",
    )


def _candidate(**kw) -> OperationalCaseCandidate:
    defaults = dict(
        candidate_id="cand_001",
        cliente_id="cli_perales",
        primary_pathology="inventario_no_confiable",
        hypothesis="Investigar si existe diferencia entre stock declarado y real.",
        available_variables=[_match()],
        evidence_gaps=[],
        status="READY_TO_INVESTIGATE",
        next_step="Evaluar.",
    )
    defaults.update(kw)
    return OperationalCaseCandidate(**defaults)


@pytest.fixture
def svc() -> CaseOpeningService:
    return CaseOpeningService()


# ---------------------------------------------------------------------------
# 1. Evidencia suficiente → READY_FOR_INVESTIGATION
# ---------------------------------------------------------------------------

def test_ready_with_available_variable(svc):
    r = svc.evaluate(_candidate())
    assert r.status == "READY_FOR_INVESTIGATION"
    assert r.clarification_question is None
    assert r.rejection_reason is None
    assert r.insufficiency_reason is None


def test_ready_with_low_gap_ignored(svc):
    low = EvidenceGap(
        gap_id="g_low", required_variable_id="v", variable_canonical_name="x",
        reason="r", impact="i", priority="LOW",
    )
    r = svc.evaluate(_candidate(evidence_gaps=[low]))
    assert r.status == "READY_FOR_INVESTIGATION"


# ---------------------------------------------------------------------------
# 2. PENDING_OWNER_VALIDATION → CLARIFICATION_REQUIRED
# ---------------------------------------------------------------------------

def test_pending_owner_validation_produces_clarification(svc):
    r = svc.evaluate(_candidate(status="PENDING_OWNER_VALIDATION"))
    assert r.status == "CLARIFICATION_REQUIRED"
    assert r.clarification_question and r.clarification_question.strip()


# ---------------------------------------------------------------------------
# 3. Brechas HIGH con fuente → CLARIFICATION_REQUIRED
# ---------------------------------------------------------------------------

def test_high_gap_with_source_produces_clarification(svc):
    r = svc.evaluate(_candidate(evidence_gaps=[_gap_high_with_src()]))
    assert r.status == "CLARIFICATION_REQUIRED"
    assert "precio_venta" in r.clarification_question


# ---------------------------------------------------------------------------
# 4. Sin variables y sin fuente → INSUFFICIENT_EVIDENCE
# ---------------------------------------------------------------------------

def test_no_variables_no_source_produces_insufficient(svc):
    r = svc.evaluate(_candidate(available_variables=[], evidence_gaps=[], status="PARTIAL_EVIDENCE"))
    assert r.status == "INSUFFICIENT_EVIDENCE"
    assert r.insufficiency_reason and r.insufficiency_reason.strip()


def test_no_variables_critical_no_src_partial_status_produces_insufficient(svc):
    """PARTIAL_EVIDENCE (no BLOCKED) + CRITICAL sin fuente → INSUFFICIENT, no REJECTED."""
    r = svc.evaluate(_candidate(
        available_variables=[],
        evidence_gaps=[_gap_critical_no_src()],
        status="PARTIAL_EVIDENCE",
    ))
    assert r.status == "INSUFFICIENT_EVIDENCE"


# ---------------------------------------------------------------------------
# 5. BLOCKED + CRITICAL sin fuente → REJECTED_OUT_OF_SCOPE
# ---------------------------------------------------------------------------

def test_blocked_critical_no_source_produces_rejected(svc):
    r = svc.evaluate(_candidate(
        available_variables=[],
        evidence_gaps=[_gap_critical_no_src()],
        status="BLOCKED_MISSING_VARIABLES",
    ))
    assert r.status == "REJECTED_OUT_OF_SCOPE"
    assert "costo_unitario" in r.rejection_reason


# ---------------------------------------------------------------------------
# 6. primary_pathology vacía → REJECTED_OUT_OF_SCOPE
# ---------------------------------------------------------------------------

def test_empty_pathology_produces_rejected(svc):
    r = svc.evaluate(_candidate(primary_pathology="   "))
    assert r.status == "REJECTED_OUT_OF_SCOPE"
    assert r.rejection_reason and "patología principal" in r.rejection_reason


# ---------------------------------------------------------------------------
# 7. case_id autogenerado como UUID
# ---------------------------------------------------------------------------

def test_case_id_autogenerated(svc):
    r = svc.evaluate(_candidate())
    assert len(r.case_id) == 36
    assert str(uuid.UUID(r.case_id)) == r.case_id


def test_case_id_explicit_preserved(svc):
    cid = str(uuid.uuid4())
    r = svc.evaluate(_candidate(), case_id=cid)
    assert r.case_id == cid


def test_two_evaluations_different_ids(svc):
    c = _candidate()
    assert svc.evaluate(c).case_id != svc.evaluate(c).case_id


# ---------------------------------------------------------------------------
# 8. Trazabilidad propagada
# ---------------------------------------------------------------------------

def test_traceability_propagated(svc):
    c = _candidate(source_admission_case_id="adm_001", source_normalized_package_id="pkg_001")
    r = svc.evaluate(c)
    assert r.candidate_id == "cand_001"
    assert r.source_admission_case_id == "adm_001"
    assert r.source_normalized_package_id == "pkg_001"
    assert r.cliente_id == "cli_perales"


# ---------------------------------------------------------------------------
# 9. Salida siempre es OperationalCase v2
# ---------------------------------------------------------------------------

def test_output_always_operational_case(svc):
    cases = [
        _candidate(),
        _candidate(status="PENDING_OWNER_VALIDATION"),
        _candidate(available_variables=[], evidence_gaps=[], status="PARTIAL_EVIDENCE"),
        _candidate(available_variables=[], evidence_gaps=[_gap_critical_no_src()],
                   status="BLOCKED_MISSING_VARIABLES"),
    ]
    valid_statuses = {
        "READY_FOR_INVESTIGATION", "CLARIFICATION_REQUIRED",
        "INSUFFICIENT_EVIDENCE", "REJECTED_OUT_OF_SCOPE",
    }
    for c in cases:
        r = svc.evaluate(c)
        assert isinstance(r, OperationalCase)
        assert r.status in valid_statuses


# ---------------------------------------------------------------------------
# 10. Sin atributos de DiagnosticReport ni FindingRecord
# ---------------------------------------------------------------------------

def test_no_diagnostic_attributes(svc):
    r = svc.evaluate(_candidate())
    for attr in ("diagnosis_status", "findings", "evidence_used",
                 "reasoning_summary", "report_id", "finding_type",
                 "measured_difference", "compared_sources"):
        assert not hasattr(r, attr)
