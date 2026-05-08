from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.contracts.clinical_operational_contracts import (
    DocumentIngestion,
    EvidenceRecord,
    FormulaExecution,
    OperationalCase,
    OperationalCaseCandidate,
    PathologyCandidate,
    ReceptionRecord,
    VariableObservation,
)


def _valid_reception(**overrides):
    payload = {
        "reception_id": "rec_001",
        "tenant_id": "tenant_demo",
        "channel": "whatsapp",
        "original_message": "Vendo mucho pero no queda plata",
        "expressed_pain": "problema de caja",
        "initial_classification": "margen_erosionado",
        "status": "RECEIVED",
        "requested_evidence_ids": [],
        "received_evidence_ids": [],
        "result_id": None,
        "blocking_reason": None,
        "detected_opportunity": None,
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return ReceptionRecord(**payload)


def _valid_evidence(**overrides):
    payload = {
        "evidence_id": "ev_001",
        "tenant_id": "tenant_demo",
        "source_type": "excel",
        "source_name": "stock_mayo.xlsx",
        "received_from": "paulita",
        "storage_ref": "s3://bucket/file.xlsx",
        "content_hash": "abc123",
        "status": "RECEIVED",
        "linked_reception_id": None,
        "quality_flags": [],
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return EvidenceRecord(**payload)


def _valid_ingestion(**overrides):
    payload = {
        "ingestion_id": "ing_001",
        "tenant_id": "tenant_demo",
        "evidence_id": "ev_001",
        "provider": "manual",
        "source_type": "excel",
        "status": "RECEIVED",
        "provider_workflow_id": None,
        "provider_call_id": None,
        "output_ref": None,
        "error_message": None,
        "quality_flags": [],
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return DocumentIngestion(**payload)


def _valid_observation(**overrides):
    payload = {
        "observation_id": "obs_001",
        "tenant_id": "tenant_demo",
        "variable_code": "margen_bruto",
        "value": 0.25,
        "unit": "ratio",
        "period": "2026-05",
        "evidence_id": "ev_001",
        "ingestion_id": "ing_001",
        "source_ref": "sheet1!A2",
        "confidence": 0.85,
        "status": "OBSERVED",
        "quality_flags": [],
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return VariableObservation(**payload)


def _valid_pathology_candidate(**overrides):
    payload = {
        "candidate_id": "pc_001",
        "tenant_id": "tenant_demo",
        "pathology_code": "margen_erosionado",
        "source_reception_id": "rec_001",
        "symptom_codes": ["s_ventas_sin_margen"],
        "supporting_observation_ids": ["obs_001"],
        "missing_evidence_codes": [],
        "confidence": 0.7,
        "status": "CANDIDATE",
        "rejection_reason": None,
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return PathologyCandidate(**payload)


def _valid_formula_execution(**overrides):
    payload = {
        "execution_id": "fx_001",
        "tenant_id": "tenant_demo",
        "formula_code": "margen_bruto_v1",
        "input_observation_ids": ["obs_001"],
        "output_variable_code": "margen_bruto",
        "result_value": None,
        "result_unit": "ratio",
        "status": "READY",
        "blocking_reason": None,
        "error_message": None,
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return FormulaExecution(**payload)


def _valid_operational_case_candidate(**overrides):
    payload = {
        "candidate_id": "occ_001",
        "tenant_id": "tenant_demo",
        "source_reception_id": "rec_001",
        "pathology_candidate_ids": ["pc_001"],
        "variable_observation_ids": ["obs_001"],
        "formula_execution_ids": ["fx_001"],
        "primary_pathology_code": "margen_erosionado",
        "evidence_gap_codes": [],
        "principal_entropic_core": "margen-caja-costos",
        "recommended_route": "ruta_1",
        "status": "DRAFT",
        "rejection_reason": None,
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return OperationalCaseCandidate(**payload)


def _valid_operational_case(**overrides):
    payload = {
        "case_id": "case_001",
        "tenant_id": "tenant_demo",
        "candidate_id": "occ_001",
        "source_reception_id": "rec_001",
        "primary_pathology_code": "margen_erosionado",
        "related_pathology_codes": ["caja_inconsistente"],
        "formula_execution_ids": ["fx_001"],
        "variable_observation_ids": ["obs_001"],
        "evidence_gap_codes": [],
        "principal_entropic_core": "margen-caja-costos",
        "recommended_route": "ruta_1",
        "status": "READY_FOR_INVESTIGATION",
        "clarification_question": None,
        "insufficiency_reason": None,
        "rejection_reason": None,
        "next_step": "Iniciar investigacion operacional.",
        "opened_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return OperationalCase(**payload)


def test_crea_reception_record_valido():
    rec = _valid_reception()

    assert rec.tenant_id == "tenant_demo"
    assert rec.status == "RECEIVED"


def test_reception_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_reception(tenant_id="   ")


def test_reception_rechaza_original_message_vacio():
    with pytest.raises(ValidationError, match="original_message"):
        _valid_reception(original_message="")


def test_reception_blocked_requiere_blocking_reason():
    with pytest.raises(ValidationError, match="blocking_reason"):
        _valid_reception(status="BLOCKED", blocking_reason=None)


def test_reception_needs_evidence_requiere_requested_evidence_ids():
    with pytest.raises(ValidationError, match="requested_evidence_ids"):
        _valid_reception(status="NEEDS_EVIDENCE", requested_evidence_ids=[])


def test_crea_evidence_record_valido():
    ev = _valid_evidence()

    assert ev.evidence_id == "ev_001"
    assert ev.status == "RECEIVED"


def test_evidence_linked_requiere_linked_reception_id():
    with pytest.raises(ValidationError, match="linked_reception_id"):
        _valid_evidence(status="LINKED", linked_reception_id=None)


def test_evidence_rejected_requiere_quality_flags():
    with pytest.raises(ValidationError, match="quality_flags"):
        _valid_evidence(status="REJECTED", quality_flags=[])


def test_source_type_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_evidence(source_type="audio")  # type: ignore[arg-type]


def test_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_reception(status="DIAGNOSTIC_CONFIRMED")  # type: ignore[arg-type]


def test_crea_document_ingestion_valido():
    ing = _valid_ingestion()

    assert ing.ingestion_id == "ing_001"
    assert ing.status == "RECEIVED"


def test_document_ingestion_rechaza_ingestion_id_vacio():
    with pytest.raises(ValidationError, match="ingestion_id"):
        _valid_ingestion(ingestion_id=" ")


def test_document_ingestion_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_ingestion(tenant_id="")


def test_document_ingestion_rechaza_evidence_id_vacio():
    with pytest.raises(ValidationError, match="evidence_id"):
        _valid_ingestion(evidence_id="  ")


def test_document_ingestion_bem_requiere_provider_call_id_en_enviado_estructurado_review():
    for status in ("SENT_TO_PROVIDER", "STRUCTURED", "NEEDS_REVIEW"):
        with pytest.raises(ValidationError, match="provider_call_id"):
            _valid_ingestion(provider="bem", status=status, provider_call_id=None)


def test_document_ingestion_structured_requiere_output_ref():
    with pytest.raises(ValidationError, match="output_ref"):
        _valid_ingestion(status="STRUCTURED", provider="manual", output_ref=None)


def test_document_ingestion_failed_requiere_error_message():
    with pytest.raises(ValidationError, match="error_message"):
        _valid_ingestion(status="FAILED", error_message="")


def test_document_ingestion_rejected_requiere_quality_flags():
    with pytest.raises(ValidationError, match="quality_flags"):
        _valid_ingestion(status="REJECTED", quality_flags=[])


def test_document_ingestion_provider_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_ingestion(provider="llm")  # type: ignore[arg-type]


def test_document_ingestion_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_ingestion(status="DONE")  # type: ignore[arg-type]


def test_document_ingestion_source_type_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_ingestion(source_type="audio")  # type: ignore[arg-type]


def test_crea_variable_observation_valida():
    obs = _valid_observation()

    assert obs.observation_id == "obs_001"
    assert obs.status == "OBSERVED"


def test_variable_observation_rechaza_observation_id_vacio():
    with pytest.raises(ValidationError, match="observation_id"):
        _valid_observation(observation_id=" ")


def test_variable_observation_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_observation(tenant_id=" ")


def test_variable_observation_rechaza_variable_code_vacio():
    with pytest.raises(ValidationError, match="variable_code"):
        _valid_observation(variable_code="")


def test_variable_observation_rechaza_evidence_id_vacio():
    with pytest.raises(ValidationError, match="evidence_id"):
        _valid_observation(evidence_id="")


def test_variable_observation_confidence_menor_a_0_falla():
    with pytest.raises(ValidationError):
        _valid_observation(confidence=-0.01)


def test_variable_observation_confidence_mayor_a_1_falla():
    with pytest.raises(ValidationError):
        _valid_observation(confidence=1.01)


def test_variable_observation_confirmed_requiere_value():
    with pytest.raises(ValidationError, match="value"):
        _valid_observation(status="CONFIRMED", value=None)


def test_variable_observation_rejected_requiere_quality_flags():
    with pytest.raises(ValidationError, match="quality_flags"):
        _valid_observation(status="REJECTED", quality_flags=[])


def test_variable_observation_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_observation(status="APPROVED")  # type: ignore[arg-type]


def test_crea_pathology_candidate_valido():
    candidate = _valid_pathology_candidate()

    assert candidate.candidate_id == "pc_001"
    assert candidate.status == "CANDIDATE"


def test_pathology_candidate_rechaza_candidate_id_vacio():
    with pytest.raises(ValidationError, match="candidate_id"):
        _valid_pathology_candidate(candidate_id=" ")


def test_pathology_candidate_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_pathology_candidate(tenant_id="")


def test_pathology_candidate_rechaza_pathology_code_vacio():
    with pytest.raises(ValidationError, match="pathology_code"):
        _valid_pathology_candidate(pathology_code=" ")


def test_pathology_candidate_confidence_menor_a_0_falla():
    with pytest.raises(ValidationError):
        _valid_pathology_candidate(confidence=-0.1)


def test_pathology_candidate_confidence_mayor_a_1_falla():
    with pytest.raises(ValidationError):
        _valid_pathology_candidate(confidence=1.1)


def test_pathology_candidate_needs_evidence_requiere_missing_evidence_codes():
    with pytest.raises(ValidationError, match="missing_evidence_codes"):
        _valid_pathology_candidate(status="NEEDS_EVIDENCE", missing_evidence_codes=[])


def test_pathology_candidate_ready_for_evaluation_requiere_supporting_observation_ids():
    with pytest.raises(ValidationError, match="supporting_observation_ids"):
        _valid_pathology_candidate(status="READY_FOR_EVALUATION", supporting_observation_ids=[])


def test_pathology_candidate_rejected_requiere_rejection_reason():
    with pytest.raises(ValidationError, match="rejection_reason"):
        _valid_pathology_candidate(status="REJECTED", rejection_reason=" ")


def test_pathology_candidate_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_pathology_candidate(status="CONFIRMED")  # type: ignore[arg-type]


def test_pathology_candidate_no_tiene_diagnostico_hallazgo_ni_accion_final():
    fields = set(PathologyCandidate.model_fields.keys())

    forbidden_fields = {
        "diagnostico_final",
        "hallazgo_final",
        "accion_recomendada_final",
        "patologia_confirmada",
    }
    assert forbidden_fields.isdisjoint(fields)


def test_crea_formula_execution_valida():
    execution = _valid_formula_execution()

    assert execution.execution_id == "fx_001"
    assert execution.status == "READY"


def test_formula_execution_rechaza_execution_id_vacio():
    with pytest.raises(ValidationError, match="execution_id"):
        _valid_formula_execution(execution_id="")


def test_formula_execution_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_formula_execution(tenant_id=" ")


def test_formula_execution_rechaza_formula_code_vacio():
    with pytest.raises(ValidationError, match="formula_code"):
        _valid_formula_execution(formula_code=" ")


def test_formula_execution_ready_requiere_input_observation_ids():
    with pytest.raises(ValidationError, match="input_observation_ids"):
        _valid_formula_execution(status="READY", input_observation_ids=[])


def test_formula_execution_executed_requiere_input_observation_ids_y_result_value():
    with pytest.raises(ValidationError, match="input_observation_ids"):
        _valid_formula_execution(status="EXECUTED", input_observation_ids=[], result_value=123)

    with pytest.raises(ValidationError, match="result_value"):
        _valid_formula_execution(status="EXECUTED", input_observation_ids=["obs_001"], result_value=None)


def test_formula_execution_blocked_requiere_blocking_reason():
    with pytest.raises(ValidationError, match="blocking_reason"):
        _valid_formula_execution(status="BLOCKED", blocking_reason="")


def test_formula_execution_failed_requiere_error_message():
    with pytest.raises(ValidationError, match="error_message"):
        _valid_formula_execution(status="FAILED", error_message=None)


def test_formula_execution_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_formula_execution(status="DONE")  # type: ignore[arg-type]


def test_formula_execution_no_tiene_diagnostico_patologia_confirmada_ni_hallazgo_final():
    fields = set(FormulaExecution.model_fields.keys())

    forbidden_fields = {
        "diagnostico_final",
        "patologia_confirmada",
        "hallazgo_final",
    }
    assert forbidden_fields.isdisjoint(fields)


def test_crea_operational_case_candidate_valido():
    candidate = _valid_operational_case_candidate()

    assert candidate.candidate_id == "occ_001"
    assert candidate.status == "DRAFT"


def test_operational_case_candidate_rechaza_candidate_id_vacio():
    with pytest.raises(ValidationError, match="candidate_id"):
        _valid_operational_case_candidate(candidate_id=" ")


def test_operational_case_candidate_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_operational_case_candidate(tenant_id=" ")


def test_operational_case_candidate_rechaza_source_reception_id_vacio():
    with pytest.raises(ValidationError, match="source_reception_id"):
        _valid_operational_case_candidate(source_reception_id=" ")


def test_operational_case_candidate_needs_evidence_requiere_evidence_gap_codes():
    with pytest.raises(ValidationError, match="evidence_gap_codes"):
        _valid_operational_case_candidate(status="NEEDS_EVIDENCE", evidence_gap_codes=[])


def test_operational_case_candidate_ready_for_review_requiere_pathology_candidate_ids():
    with pytest.raises(ValidationError, match="pathology_candidate_ids"):
        _valid_operational_case_candidate(status="READY_FOR_REVIEW", pathology_candidate_ids=[])


def test_operational_case_candidate_ready_for_review_requiere_variable_observation_ids():
    with pytest.raises(ValidationError, match="variable_observation_ids"):
        _valid_operational_case_candidate(status="READY_FOR_REVIEW", variable_observation_ids=[])


def test_operational_case_candidate_ready_for_review_requiere_formula_execution_ids():
    with pytest.raises(ValidationError, match="formula_execution_ids"):
        _valid_operational_case_candidate(status="READY_FOR_REVIEW", formula_execution_ids=[])


def test_operational_case_candidate_ready_for_review_requiere_primary_pathology_code():
    with pytest.raises(ValidationError, match="primary_pathology_code"):
        _valid_operational_case_candidate(status="READY_FOR_REVIEW", primary_pathology_code=None)


def test_operational_case_candidate_ready_for_review_requiere_principal_entropic_core():
    with pytest.raises(ValidationError, match="principal_entropic_core"):
        _valid_operational_case_candidate(status="READY_FOR_REVIEW", principal_entropic_core=None)


def test_operational_case_candidate_rejected_requiere_rejection_reason():
    with pytest.raises(ValidationError, match="rejection_reason"):
        _valid_operational_case_candidate(status="REJECTED", rejection_reason="")


def test_operational_case_candidate_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_operational_case_candidate(status="APPROVED")  # type: ignore[arg-type]


def test_operational_case_candidate_no_tiene_diagnostico_final_ni_hallazgo_final():
    fields = set(OperationalCaseCandidate.model_fields.keys())
    forbidden_fields = {"diagnostico_final", "hallazgo_final", "accion_recomendada_final"}
    assert forbidden_fields.isdisjoint(fields)


def test_crea_operational_case_valido_ready_for_investigation():
    case = _valid_operational_case()

    assert case.case_id == "case_001"
    assert case.status == "READY_FOR_INVESTIGATION"


def test_operational_case_rechaza_case_id_vacio():
    with pytest.raises(ValidationError, match="case_id"):
        _valid_operational_case(case_id=" ")


def test_operational_case_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_operational_case(tenant_id="")


def test_operational_case_rechaza_candidate_id_vacio():
    with pytest.raises(ValidationError, match="candidate_id"):
        _valid_operational_case(candidate_id=" ")


def test_operational_case_rechaza_source_reception_id_vacio():
    with pytest.raises(ValidationError, match="source_reception_id"):
        _valid_operational_case(source_reception_id="")


def test_operational_case_rechaza_primary_pathology_code_vacio():
    with pytest.raises(ValidationError, match="primary_pathology_code"):
        _valid_operational_case(primary_pathology_code=" ")


def test_operational_case_rechaza_next_step_vacio():
    with pytest.raises(ValidationError, match="next_step"):
        _valid_operational_case(next_step=" ")


def test_operational_case_ready_for_investigation_requiere_variable_observation_ids():
    with pytest.raises(ValidationError, match="variable_observation_ids"):
        _valid_operational_case(status="READY_FOR_INVESTIGATION", variable_observation_ids=[])


def test_operational_case_ready_for_investigation_requiere_formula_execution_ids():
    with pytest.raises(ValidationError, match="formula_execution_ids"):
        _valid_operational_case(status="READY_FOR_INVESTIGATION", formula_execution_ids=[])


def test_operational_case_ready_for_investigation_requiere_principal_entropic_core():
    with pytest.raises(ValidationError, match="principal_entropic_core"):
        _valid_operational_case(status="READY_FOR_INVESTIGATION", principal_entropic_core=None)


def test_operational_case_ready_for_investigation_requiere_opened_at():
    with pytest.raises(ValidationError, match="opened_at"):
        _valid_operational_case(status="READY_FOR_INVESTIGATION", opened_at=None)


def test_operational_case_clarification_required_requiere_clarification_question():
    with pytest.raises(ValidationError, match="clarification_question"):
        _valid_operational_case(
            status="CLARIFICATION_REQUIRED",
            clarification_question=None,
            opened_at=None,
            variable_observation_ids=[],
            formula_execution_ids=[],
            principal_entropic_core=None,
        )


def test_operational_case_insufficient_evidence_requiere_insufficiency_reason():
    with pytest.raises(ValidationError, match="insufficiency_reason"):
        _valid_operational_case(
            status="INSUFFICIENT_EVIDENCE",
            insufficiency_reason="",
            opened_at=None,
            variable_observation_ids=[],
            formula_execution_ids=[],
            principal_entropic_core=None,
        )


def test_operational_case_rejected_out_of_scope_requiere_rejection_reason():
    with pytest.raises(ValidationError, match="rejection_reason"):
        _valid_operational_case(
            status="REJECTED_OUT_OF_SCOPE",
            rejection_reason=" ",
            opened_at=None,
            variable_observation_ids=[],
            formula_execution_ids=[],
            principal_entropic_core=None,
        )


def test_operational_case_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_operational_case(status="OPEN")  # type: ignore[arg-type]


def test_operational_case_no_tiene_hallazgo_final_accion_ejecutada_ni_decision_automatica():
    fields = set(OperationalCase.model_fields.keys())
    forbidden_fields = {"hallazgo_final", "accion_ejecutada", "decision_automatica_dueno"}
    assert forbidden_fields.isdisjoint(fields)



def test_contratos_no_tienen_campos_de_diagnostico_ni_hallazgo_final():
    reception_fields = set(ReceptionRecord.model_fields.keys())
    evidence_fields = set(EvidenceRecord.model_fields.keys())
    ingestion_fields = set(DocumentIngestion.model_fields.keys())
    observation_fields = set(VariableObservation.model_fields.keys())
    pathology_fields = set(PathologyCandidate.model_fields.keys())
    formula_fields = set(FormulaExecution.model_fields.keys())
    candidate_fields = set(OperationalCaseCandidate.model_fields.keys())
    case_fields = set(OperationalCase.model_fields.keys())

    forbidden_fields = {
        "diagnostico_final",
        "diagnostico_emitido",
        "finding_record",
        "hallazgo_final",
        "hallazgo_confirmado",
        "patologia_final",
    }

    assert forbidden_fields.isdisjoint(reception_fields)
    assert forbidden_fields.isdisjoint(evidence_fields)
    assert forbidden_fields.isdisjoint(ingestion_fields)
    assert forbidden_fields.isdisjoint(observation_fields)
    assert forbidden_fields.isdisjoint(pathology_fields)
    assert forbidden_fields.isdisjoint(formula_fields)
    assert forbidden_fields.isdisjoint(candidate_fields)
    assert forbidden_fields.isdisjoint(case_fields)
