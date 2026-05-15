"""
Tests para el formatter de respuesta del pipeline de admisión v1.
"""
import uuid
import pytest
from app.contracts.admission_v1 import DDIArtifact, SymptomNode, HypothesisNode
from app.pipeline.admission.v1.response_formatter import AdmissionResponseFormatterV1


@pytest.fixture
def formatter() -> AdmissionResponseFormatterV1:
    return AdmissionResponseFormatterV1()

@pytest.fixture
def sample_artifact() -> DDIArtifact:
    """
    Crea un DDIArtifact de ejemplo para usar en los tests.
    Simula la salida del pipeline para el claim "vendo mucho pero no queda plata".
    """
    pyme_id = uuid.uuid4()
    symptom = SymptomNode(claim="vendemos mucho pero no queda plata")
    
    h1 = HypothesisNode(description="Tensión de caja", confidence_score=4.5, evidence_required=["ventas", "costos"])
    h2 = HypothesisNode(description="Margen erosionado", confidence_score=3.0, evidence_required=["ventas", "lista de precios"])
    h3 = HypothesisNode(description="Fuga operativa", confidence_score=3.0, evidence_required=["costos", "movimientos de caja"])

    hypotheses = [h1, h2, h3]
    
    return DDIArtifact(
        pyme_id=pyme_id,
        symptoms=[symptom],
        hypotheses=hypotheses,
        primary_hypothesis_id=h1.node_id
    )


def test_formatter_includes_symptom(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert "Registré este síntoma operacional: vendemos mucho pero no queda plata." in response

def test_formatter_includes_primary_hypothesis(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert """Hipótesis inicial prioritaria:
tensión de caja.""" in response

def test_formatter_includes_other_hypotheses(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert """También quedan abiertas:
margen erosionado, fuga operativa.""" in response

def test_formatter_includes_evidence(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    # El orden es importante por el sorted() en el formatter
    expected_evidence = "costos, lista de precios, movimientos de caja, ventas"
    assert f"""Para confirmar o refutar estas hipótesis necesito:
{expected_evidence}.""" in response

def test_formatter_adheres_to_style_guide(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert "Hermes" not in response
    assert "diagnóstico" not in response # No debe afirmar un diagnóstico
    assert "confirmado" not in response
    assert "hecho" not in response

def test_formatter_no_hypotheses_returns_none(formatter: AdmissionResponseFormatterV1):
    pyme_id = uuid.uuid4()
    artifact = DDIArtifact(
        pyme_id=pyme_id,
        symptoms=[SymptomNode(claim="un síntoma sin hipótesis")]
    )
    response = formatter.format_response(artifact)
    assert response is None
