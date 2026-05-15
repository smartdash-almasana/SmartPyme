"""
Tests para los contratos de admisión v1.
"""
import pytest
from pydantic import ValidationError
import uuid

from app.contracts.admission_v1 import (
    FichaIdentidadOperacional,
    SymptomNode,
    HypothesisNode,
    FactNode,
    TensionNode,
    DDIArtifact,
    AdmissionState,
    NodeType
)


def test_ficha_identidad_operacional_creation():
    """
    Valida la creación y serialización de FichaIdentidadOperacional.
    """
    pyme_id = uuid.uuid4()
    ficha = FichaIdentidadOperacional(
        pyme_id=pyme_id,
        nombre_fiscal="Mi Pyme S.L.",
        nif="B12345678",
        sector="Retail"
    )
    assert ficha.pyme_id == pyme_id
    assert ficha.nombre_fiscal == "Mi Pyme S.L."
    assert ficha.nif == "B12345678"
    assert ficha.sector == "Retail"
    
    # Check serialization
    assert "pyme_id" in ficha.model_dump()


def test_symptom_node_creation():
    """
    Valida la creación de un SymptomNode.
    """
    node = SymptomNode(
        claim="Vendemos mucho pero no queda plata.",
        intensity="high",
        temporalidad="a fin de mes"
    )
    assert node.node_type == NodeType.SYMPTOM
    assert node.claim == "Vendemos mucho pero no queda plata."
    assert node.intensity == "high"
    assert isinstance(node.node_id, uuid.UUID)


def test_hypothesis_node_creation():
    """
    Valida la creación de un HypothesisNode.
    """
    node = HypothesisNode(
        description="Posible fuga de margen en productos clave.",
        evidence_required=["informe_ventas_por_producto", "lista_de_precios_proveedores"]
    )
    assert node.node_type == NodeType.HYPOTHESIS
    assert "informe_ventas_por_producto" in node.evidence_required
    assert isinstance(node.node_id, uuid.UUID)


def test_fact_node_creation():
    """
    Valida la creación de un FactNode.
    """
    node = FactNode(
        description="El margen bruto del producto 'X' es del 15%.",
        source_id="doc_id_1234"
    )
    assert node.node_type == NodeType.FACT
    assert node.source_id == "doc_id_1234"
    assert isinstance(node.node_id, uuid.UUID)


def test_tension_node_creation():
    """
    Valida la creación de un TensionNode.
    """
    symptom_id = uuid.uuid4()
    fact_id = uuid.uuid4()
    node = TensionNode(
        description="El cliente percibe baja rentabilidad (síntoma) pero el margen bruto es alto (hecho).",
        node_ids=[symptom_id, fact_id]
    )
    assert node.node_type == NodeType.TENSION
    assert len(node.node_ids) == 2
    assert symptom_id in node.node_ids
    assert fact_id in node.node_ids


def test_tension_node_requires_at_least_two_nodes():
    """
    Valida que TensionNode requiera al menos dos nodos en tensión.
    """
    with pytest.raises(ValidationError):
        TensionNode(
            description="No se puede tener una tensión con un solo nodo.",
            node_ids=[uuid.uuid4()]
        )


def test_ddi_artifact_creation():
    """
    Valida la creación de un DDIArtifact.
    """
    pyme_id = uuid.uuid4()
    symptom = SymptomNode(claim="No llego a fin de mes.")
    hypothesis = HypothesisNode(description="Problema de flujo de caja.")
    
    artifact = DDIArtifact(
        pyme_id=pyme_id,
        symptoms=[symptom],
        hypotheses=[hypothesis]
    )
    assert artifact.pyme_id == pyme_id
    assert len(artifact.symptoms) == 1
    assert artifact.symptoms[0].claim == "No llego a fin de mes."
    assert len(artifact.hypotheses) == 1


def test_admission_state_creation_and_validation():
    """
    Valida la creación y los estados epistemológicos de AdmissionState.
    """
    pyme_id = uuid.uuid4()
    state = AdmissionState(
        pyme_id=pyme_id,
        state="hypotheses_generated",
        details="Se han generado hipótesis iniciales. Se requiere evidencia."
    )
    assert state.state == "hypotheses_generated"
    assert state.pyme_id == pyme_id

    # Test invalid state
    with pytest.raises(ValidationError):
        AdmissionState(
            pyme_id=pyme_id,
            state="estado_invalido",
            details="Este estado no debería ser válido."
        )

