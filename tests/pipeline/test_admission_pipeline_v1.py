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

    # 1. Validar SymptomNode
    assert len(artifact.symptoms) == 1
    symptom = artifact.symptoms[0]
    assert symptom.node_type == NodeType.SYMPTOM
    assert symptom.claim == claim

    # 2. Validar HypothesisNodes
    assert len(artifact.hypotheses) == 3
    descriptions = {h.description for h in artifact.hypotheses}
    assert "Tensión de caja" in descriptions
    assert "Fuga operativa" in descriptions
    assert "Margen erosionado" in descriptions

    # 3. Validar Evidencia Requerida
    evidence = set()
    for h in artifact.hypotheses:
        evidence.update(h.evidence_required)
    
    expected_evidence = {"ventas", "costos", "movimientos de caja", "extractos", "lista de precios si aplica"}
    assert evidence == expected_evidence


def test_pipeline_generates_valid_admission_state(pipeline: AdmissionPipelineV1):
    """
    Valida que el pipeline genere un AdmissionState válido.
    """
    pyme_id = uuid.uuid4()
    claim = "vendemos mucho pero no queda plata"

    _, state = pipeline.run(pyme_id=pyme_id, claim=claim)

    assert state is not None
    assert isinstance(state, AdmissionState)
    assert state.pyme_id == pyme_id
    assert state.state == "hypotheses_generated"
    assert "Se generaron 3 hipótesis" in state.details


def test_pipeline_no_hypotheses_generated(pipeline: AdmissionPipelineV1):
    """
    Valida el comportamiento cuando no se encuentra ninguna heurística.
    """
    pyme_id = uuid.uuid4()
    claim = "un problema completamente nuevo y desconocido"

    artifact, state = pipeline.run(pyme_id=pyme_id, claim=claim)

    assert len(artifact.symptoms) == 1
    assert artifact.symptoms[0].claim == claim
    assert len(artifact.hypotheses) == 0

    assert state is not None
    assert state.state == "symptoms_captured"


@pytest.mark.parametrize("claim", [
    "vendemos mucho pero no queda plata",
    "vendo y no queda nada",
    "entra plata y desaparece",
    "trabajamos mucho y no vemos ganancias",
    "facturo bastante pero no sé si gano",
    "Mercado Libre vende pero no sé si deja margen",
])
def test_pipeline_handles_claim_variations(pipeline: AdmissionPipelineV1, claim: str):
    """
    Valida que diferentes variaciones de un mismo síntoma generen el mismo set de hipótesis.
    """
    pyme_id = uuid.uuid4()
    artifact, _ = pipeline.run(pyme_id=pyme_id, claim=claim)

    # Validar que se generen las 3 hipótesis esperadas
    assert len(artifact.hypotheses) == 3
    descriptions = {h.description for h in artifact.hypotheses}
    assert "Tensión de caja" in descriptions
    assert "Fuga operativa" in descriptions
    assert "Margen erosionado" in descriptions

    # Validar la evidencia requerida
    evidence = {e for h in artifact.hypotheses for e in h.evidence_required}
    expected_evidence = {"ventas", "costos", "movimientos de caja", "extractos", "lista de precios si aplica"}
    assert evidence == expected_evidence

