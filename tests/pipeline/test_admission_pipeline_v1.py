"""
Tests para el pipeline de admisión v1.
"""
import uuid
import pytest
from app.pipeline.admission.v1.pipeline import AdmissionPipelineV1
from app.contracts.admission_v1 import NodeType, AdmissionState


@pytest.fixture
def pipeline() -> AdmissionPipelineV1:
    """
    Fixture que retorna una instancia del pipeline de admisión.
    """
    return AdmissionPipelineV1()


def test_pipeline_specific_claim_to_symptom_and_hypotheses(pipeline: AdmissionPipelineV1):
    """
    Valida que un claim específico genere el SymptomNode y las HypothesisNode correctas.
    """
    pyme_id = uuid.uuid4()
    claim = "vendemos mucho pero no queda plata"

    artifact, _ = pipeline.run(pyme_id=pyme_id, claim=claim)

    assert len(artifact.symptoms) == 1
    symptom = artifact.symptoms[0]
    assert symptom.node_type == NodeType.SYMPTOM
    assert symptom.claim == claim

    assert len(artifact.hypotheses) == 3
    descriptions = {h.description for h in artifact.hypotheses}
    assert "Tensión de caja" in descriptions

    evidence = {e for h in artifact.hypotheses for e in h.evidence_required}
    expected_evidence = {"ventas", "costos", "movimientos de caja", "extractos", "lista de precios si aplica"}
    assert evidence == expected_evidence
    
    # Validar que el score sea mayor a 0
    assert artifact.hypotheses[0].confidence_score > 0


def test_pipeline_generates_valid_admission_state(pipeline: AdmissionPipelineV1):
    """
    Valida que el pipeline genere un AdmissionState válido.
    """
    pyme_id = uuid.uuid4()
    claim = "vendemos mucho pero no queda plata"

    _, state = pipeline.run(pyme_id=pyme_id, claim=claim)

    assert state is not None
    assert state.state == "hypotheses_generated"
    assert "La hipótesis principal es" in state.details


def test_pipeline_no_hypotheses_generated(pipeline: AdmissionPipelineV1):
    """
    Valida el comportamiento cuando no se encuentra ninguna heurística.
    """
    pyme_id = uuid.uuid4()
    claim = "un problema completamente nuevo y desconocido"

    artifact, state = pipeline.run(pyme_id=pyme_id, claim=claim)

    assert len(artifact.hypotheses) == 0
    assert artifact.primary_hypothesis_id is None
    assert state.state == "symptoms_captured"


@pytest.mark.parametrize("claim", [
    "vendo y no queda nada",
    "trabajamos mucho y no vemos ganancias",
])
def test_pipeline_handles_profit_claim_variations(pipeline: AdmissionPipelineV1, claim: str):
    """
    Valida que diferentes variaciones de un mismo síntoma generen el mismo set de hipótesis.
    """
    pyme_id = uuid.uuid4()
    artifact, _ = pipeline.run(pyme_id=pyme_id, claim=claim)

    assert len(artifact.hypotheses) == 3
    assert artifact.primary_hypothesis_id is not None
    assert artifact.primary_hypothesis_id == artifact.hypotheses[0].node_id


@pytest.mark.parametrize("claim", [
    "tengo mucho stock parado",
    "me falta stock de lo que más vendo",
])
def test_pipeline_handles_inventory_claim_variations(pipeline: AdmissionPipelineV1, claim: str):
    """
    Valida que diferentes variaciones de síntomas de inventario generen el mismo set de hipótesis.
    """
    pyme_id = uuid.uuid4()
    artifact, _ = pipeline.run(pyme_id=pyme_id, claim=claim)

    assert len(artifact.hypotheses) == 4
    assert artifact.primary_hypothesis_id is not None
    assert artifact.primary_hypothesis_id == artifact.hypotheses[0].node_id


def test_pipeline_handles_mixed_claim(pipeline: AdmissionPipelineV1):
    """
    Valida que un claim con síntomas mezclados genere hipótesis de ambos clusters,
    y que la priorización sea correcta.
    """
    pyme_id = uuid.uuid4()
    claim = "vendo mucho pero no queda plata y además tengo stock clavado"

    artifact, _ = pipeline.run(pyme_id=pyme_id, claim=claim)

    # 3 hipótesis de rentabilidad + 4 de inventario
    assert len(artifact.hypotheses) == 7

    descriptions = {h.description for h in artifact.hypotheses}
    assert "Tensión de caja" in descriptions
    assert "Stock inmovilizado" in descriptions

    # Validar que estén ordenadas por score
    scores = [h.confidence_score for h in artifact.hypotheses]
    assert scores == sorted(scores, reverse=True)

    # Validar que la hipótesis primaria sea la de mayor score
    assert artifact.primary_hypothesis_id == artifact.hypotheses[0].node_id

    # En este caso, el cluster de rentabilidad debería tener mayor score
    # (verb + noun + pain = 1.0 + 1.5 + 2.0 = 4.5)
    # vs inventario (noun + pain = 1.5 + 2.0 = 3.5)
    assert artifact.hypotheses[0].description in {"Tensión de caja", "Fuga operativa", "Margen erosionado"}

    # Validar la traza de razonamiento
    primary_hypo = artifact.hypotheses[0]
    assert len(primary_hypo.reasoning_trace) > 0
    assert "vendo" in primary_hypo.reasoning_trace
    assert "no queda plata" in primary_hypo.reasoning_trace

    inventory_hypo = next(h for h in artifact.hypotheses if h.description == "Stock inmovilizado")
    assert "stock" in inventory_hypo.reasoning_trace
    assert "clavado" in inventory_hypo.reasoning_trace
