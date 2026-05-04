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
    IntentType,
    OwnerDemand,
    OwnerDemandCandidate,
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


# ---------------------------------------------------------------------------
# Tests TS_ADM_003: OwnerDemandCandidate e IntentType
# ---------------------------------------------------------------------------


def test_owner_demand_candidate_valid():
    """OwnerDemandCandidate válido debe construirse sin errores."""
    candidate = OwnerDemandCandidate(
        case_id="case_perales_001",
        raw_text="No sé cuánto stock tengo. Paulita tiene un Excel.",
        explicit_objective="Entender cuánto stock tengo y si los precios están bien",
        intent_type="QUIERE_ENTENDER",
        area_hint="stock",
        urgency=3,
        clarification_needed=False,
    )

    assert candidate.case_id == "case_perales_001"
    assert candidate.intent_type == "QUIERE_ENTENDER"
    assert candidate.area_hint == "stock"
    assert candidate.urgency == 3
    assert candidate.clarification_needed is False
    assert candidate.clarification_question is None


def test_owner_demand_candidate_demand_id_autogenerated():
    """demand_id debe autogenerarse como UUID válido si no se pasa."""
    import uuid as _uuid

    candidate = OwnerDemandCandidate(
        case_id="case_x",
        raw_text="Texto de prueba",
        intent_type="QUIERE_ACTUAR",
    )

    assert candidate.demand_id != ""
    assert len(candidate.demand_id) == 36
    parsed = _uuid.UUID(candidate.demand_id)
    assert str(parsed) == candidate.demand_id


def test_owner_demand_candidate_raw_text_empty_fails():
    """raw_text vacío debe lanzar ValidationError."""
    with pytest.raises(ValidationError, match="vacío"):
        OwnerDemandCandidate(
            case_id="case_x",
            raw_text="   ",  # solo espacios
            intent_type="QUIERE_ENTENDER",
        )


def test_owner_demand_candidate_raw_text_empty_string_fails():
    """raw_text string vacío debe lanzar ValidationError."""
    with pytest.raises(ValidationError, match="vacío"):
        OwnerDemandCandidate(
            case_id="case_x",
            raw_text="",
            intent_type="QUIERE_ENTENDER",
        )


def test_owner_demand_candidate_urgency_out_of_range_fails():
    """urgency fuera de [1, 5] debe lanzar ValidationError."""
    with pytest.raises(ValidationError, match="urgency"):
        OwnerDemandCandidate(
            case_id="case_x",
            raw_text="Texto válido",
            intent_type="QUIERE_ENTENDER",
            urgency=0,
        )

    with pytest.raises(ValidationError, match="urgency"):
        OwnerDemandCandidate(
            case_id="case_x",
            raw_text="Texto válido",
            intent_type="QUIERE_ENTENDER",
            urgency=6,
        )


def test_owner_demand_candidate_clarification_needed_without_question_fails():
    """clarification_needed=True sin clarification_question debe fallar."""
    with pytest.raises(ValidationError, match="clarification_question"):
        OwnerDemandCandidate(
            case_id="case_x",
            raw_text="Texto válido",
            intent_type="QUIERE_ENTENDER",
            clarification_needed=True,
            clarification_question=None,
        )


def test_owner_demand_candidate_clarification_needed_with_question_passes():
    """clarification_needed=True con clarification_question debe pasar."""
    candidate = OwnerDemandCandidate(
        case_id="case_x",
        raw_text="No me dan los números",
        intent_type="QUIERE_ENTENDER",
        clarification_needed=True,
        clarification_question="¿Qué área querés revisar primero: ventas, stock o caja?",
    )
    assert candidate.clarification_needed is True
    assert candidate.clarification_question is not None


def test_intent_type_accepts_all_five_values():
    """IntentType debe aceptar los 5 valores válidos."""
    valid_intents = [
        "QUIERE_ENTENDER",
        "QUIERE_ACTUAR",
        "QUIERE_SUBIR_EVIDENCIA",
        "QUIERE_AUTORIZAR",
        "QUIERE_CONSULTAR_ESTADO",
    ]
    for intent in valid_intents:
        candidate = OwnerDemandCandidate(
            case_id="case_x",
            raw_text="Texto de prueba",
            intent_type=intent,  # type: ignore[arg-type]
        )
        assert candidate.intent_type == intent


def test_intent_type_rejects_invalid_value():
    """IntentType con valor inválido debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        OwnerDemandCandidate(
            case_id="case_x",
            raw_text="Texto de prueba",
            intent_type="QUIERE_DIAGNOSTICAR",  # type: ignore[arg-type]
        )


def test_initial_case_admission_accepts_hint_fields():
    """InitialCaseAdmission debe aceptar clinical_phase_hint, symptoms_hint y pathologies_hint."""
    admission = InitialCaseAdmission(
        case_id="case_hints_001",
        cliente_id="cliente_x",
        demand=_valid_demand(),
        clinical_phase="INESTABILIDAD",
        next_step="Pedir Excel a Paulita.",
        clinical_phase_hint="INESTABILIDAD",
        symptoms_hint=["stock_desordenado", "precios_desactualizados"],
        pathologies_hint=["inventario_no_confiable"],
    )

    assert admission.clinical_phase_hint == "INESTABILIDAD"
    assert "stock_desordenado" in admission.symptoms_hint
    assert "inventario_no_confiable" in admission.pathologies_hint


def test_initial_case_admission_hint_fields_default_to_empty():
    """Los campos *_hint deben tener valores por defecto vacíos."""
    admission = InitialCaseAdmission(
        case_id="case_defaults",
        cliente_id="cliente_x",
        demand=_valid_demand(),
        clinical_phase="OPTIMIZACION",
        next_step="Siguiente paso.",
    )

    assert admission.clinical_phase_hint is None
    assert admission.symptoms_hint == []
    assert admission.pathologies_hint == []
    assert admission.owner_demand_candidate is None


def test_initial_case_admission_with_owner_demand_candidate():
    """InitialCaseAdmission debe aceptar owner_demand_candidate."""
    candidate = OwnerDemandCandidate(
        case_id="case_odc_001",
        raw_text="No sé cuánto stock tengo.",
        intent_type="QUIERE_ENTENDER",
        area_hint="stock",
    )
    admission = InitialCaseAdmission(
        case_id="case_odc_001",
        cliente_id="cliente_x",
        demand=_valid_demand(),
        clinical_phase="INESTABILIDAD",
        next_step="Pedir Excel.",
        owner_demand_candidate=candidate,
    )

    assert admission.owner_demand_candidate is not None
    assert admission.owner_demand_candidate.intent_type == "QUIERE_ENTENDER"
