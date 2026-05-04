"""
Tests — Contratos Pydantic Capa 1: Admisión Epistemológica
TS_ADM_001_CONTRATOS_ADMISION

Valida los contratos definidos en app/contracts/admission_contract.py.

Cobertura requerida:
  1. Construir InitialCaseAdmission válido completo.
  2. EvidenceItem.confidence rechaza valores < 0 y > 1.
  3. OwnerDemand.urgency rechaza valores < 1 y > 5.
  4. ClinicalPhase rechaza valores inválidos.
  5. EpistemicState rechaza valores inválidos.
  6. EvidenceTask.status queda PENDING por defecto.
"""

import pytest
from pydantic import ValidationError

from app.contracts.admission_contract import (
    EvidenceItem,
    EvidenceTask,
    InitialCaseAdmission,
    OwnerDemand,
    PathologyCandidate,
    Person,
    Source,
    SymptomCandidate,
)


# ---------------------------------------------------------------------------
# Fixtures de objetos mínimos válidos
# ---------------------------------------------------------------------------


def _valid_demand() -> OwnerDemand:
    return OwnerDemand(
        raw_text="No sé cuánto stock tengo ni los precios.",
        explicit_objective="Ordenar stock y precios",
        area="stock",
        urgency=3,
    )


def _valid_evidence_item() -> EvidenceItem:
    return EvidenceItem(
        evidence_id="ev_001",
        evidence_type="Excel_stock",
        epistemic_state="DUDA",
        confidence=0.5,
    )


def _valid_evidence_task() -> EvidenceTask:
    return EvidenceTask(
        task_id="task_001",
        task_type="REQUEST_EVIDENCE",
        evidence_id="ev_001",
        instruction="Pedirle a Paulita el Excel de stock y precios.",
    )


# ---------------------------------------------------------------------------
# Test 1: Construir InitialCaseAdmission válido completo
# ---------------------------------------------------------------------------


def test_initial_case_admission_valid_construction():
    """Un InitialCaseAdmission bien formado debe construirse sin errores."""
    admission = InitialCaseAdmission(
        case_id="case_perales_001",
        cliente_id="cliente_perales",
        demand=_valid_demand(),
        clinical_phase="INESTABILIDAD",
        people=[
            Person(
                person_id="person_001",
                name="Paulita",
                role="Administración interna",
            )
        ],
        sources=[
            Source(
                source_id="src_001",
                source_type="excel",
                owner_person_id="person_001",
            )
        ],
        evidence=[_valid_evidence_item()],
        tasks=[_valid_evidence_task()],
        symptoms=[
            SymptomCandidate(symptom_id="stock_desordenado", confidence=0.9)
        ],
        pathologies=[
            PathologyCandidate(
                pathology_id="inventario_no_confiable",
                score=0.8,
                reason="Stock declarado sin conteo físico confirmado.",
            )
        ],
        next_step="Pedir a Paulita el Excel de stock y precios antes de avanzar.",
    )

    assert admission.case_id == "case_perales_001"
    assert admission.cliente_id == "cliente_perales"
    assert admission.clinical_phase == "INESTABILIDAD"
    assert len(admission.people) == 1
    assert len(admission.sources) == 1
    assert len(admission.evidence) == 1
    assert len(admission.tasks) == 1
    assert len(admission.symptoms) == 1
    assert len(admission.pathologies) == 1
    assert admission.next_step != ""


# ---------------------------------------------------------------------------
# Test 2: EvidenceItem.confidence rechaza < 0 y > 1
# ---------------------------------------------------------------------------


def test_evidence_item_confidence_rejects_below_zero():
    """confidence < 0 debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        EvidenceItem(
            evidence_id="ev_bad",
            evidence_type="Excel_stock",
            epistemic_state="CERTEZA",
            confidence=-0.1,
        )


def test_evidence_item_confidence_rejects_above_one():
    """confidence > 1 debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        EvidenceItem(
            evidence_id="ev_bad",
            evidence_type="Excel_stock",
            epistemic_state="CERTEZA",
            confidence=1.1,
        )


# ---------------------------------------------------------------------------
# Test 3: OwnerDemand.urgency rechaza < 1 y > 5
# ---------------------------------------------------------------------------


def test_owner_demand_urgency_rejects_below_one():
    """urgency < 1 debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        OwnerDemand(
            raw_text="Texto",
            explicit_objective="Objetivo",
            area="caja",
            urgency=0,
        )


def test_owner_demand_urgency_rejects_above_five():
    """urgency > 5 debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        OwnerDemand(
            raw_text="Texto",
            explicit_objective="Objetivo",
            area="caja",
            urgency=6,
        )


# ---------------------------------------------------------------------------
# Test 4: ClinicalPhase rechaza valores inválidos
# ---------------------------------------------------------------------------


def test_clinical_phase_rejects_invalid_value():
    """clinical_phase con valor fuera del Literal debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        InitialCaseAdmission(
            case_id="case_x",
            cliente_id="cliente_x",
            demand=_valid_demand(),
            clinical_phase="CRISIS",  # type: ignore[arg-type]
            next_step="Siguiente paso.",
        )


# ---------------------------------------------------------------------------
# Test 5: EpistemicState rechaza valores inválidos
# ---------------------------------------------------------------------------


def test_epistemic_state_rejects_invalid_value():
    """epistemic_state con valor fuera del Literal debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        EvidenceItem(
            evidence_id="ev_bad",
            evidence_type="Excel_stock",
            epistemic_state="SOSPECHA",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Test 6: EvidenceTask.status queda PENDING por defecto
# ---------------------------------------------------------------------------


def test_evidence_task_status_defaults_to_pending():
    """EvidenceTask sin status explícito debe tener status='PENDING'."""
    task = EvidenceTask(
        task_id="task_default",
        task_type="REQUEST_EVIDENCE",
        evidence_id="ev_001",
        instruction="Pedir archivo.",
    )
    assert task.status == "PENDING"
