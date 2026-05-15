"""
Contratos de Admisión v1 para el Laboratorio Pyme.

Estos modelos Pydantic definen la estructura de datos para la fase de admisión,
donde se captura la narrativa inicial del cliente y se transforma en nodos
epistemológicos estructurados.
"""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, UUID4, conlist
import uuid


class FichaIdentidadOperacional(BaseModel):
    """
    Representa la identidad operacional de la Pyme sujeta a análisis.
    """
    pyme_id: UUID4 = Field(default_factory=uuid.uuid4, description="ID único de la Pyme.")
    nombre_fiscal: str = Field(..., description="Nombre fiscal de la Pyme.")
    nif: str = Field(..., description="NIF o identificador fiscal de la Pyme.")
    sector: str | None = Field(None, description="Sector de actividad de la Pyme.")


class NodeType(str, Enum):
    """
    Tipos de nodos epistemológicos utilizados en el grafo de admisión.
    """
    SYMPTOM = "symptom"
    HYPOTHESIS = "hypothesis"
    FACT = "fact"
    TENSION = "tension"


class SymptomNode(BaseModel):
    """

    Representa un síntoma o 'dolor' declarado por el cliente.
    Es una pieza de información subjetiva que necesita ser validada.
    """
    node_id: UUID4 = Field(default_factory=uuid.uuid4)
    node_type: Literal[NodeType.SYMPTOM] = NodeType.SYMPTOM
    claim: str = Field(..., description="La declaración literal del cliente sobre el síntoma.")
    intensity: Literal["low", "medium", "high"] | None = Field(None, description="Intensidad percibida del síntoma.")
    temporalidad: str | None = Field(None, description="Descripción de cuándo ocurre el síntoma (e.g., 'a fin de mes').")


class HypothesisNode(BaseModel):
    """
    Representa una hipótesis de trabajo que intenta explicar uno o más síntomas.
    Esta hipótesis debe ser verificada con evidencia (hechos).
    """
    node_id: UUID4 = Field(default_factory=uuid.uuid4)
    node_type: Literal[NodeType.HYPOTHESIS] = NodeType.HYPOTHESIS
    description: str = Field(..., description="Descripción de la hipótesis.")
    evidence_required: list[str] = Field(default_factory=list, description="Lista de evidencia necesaria para validar la hipótesis.")


class FactNode(BaseModel):
    """
    Representa un hecho verificable y objetivo, usualmente extraído de
    un documento o sistema externo. Es la evidencia que soporta o refuta
    una hipótesis.
    """
    node_id: UUID4 = Field(default_factory=uuid.uuid4)
    node_type: Literal[NodeType.FACT] = NodeType.FACT
    description: str = Field(..., description="Descripción del hecho.")
    source_id: str = Field(..., description="ID del documento o fuente de donde se extrajo el hecho.")


class TensionNode(BaseModel):
    """
    Representa una tensión o contradicción detectada entre dos o más nodos.
    Por ejemplo, una contradicción entre un síntoma y un hecho.
    """
    node_id: UUID4 = Field(default_factory=uuid.uuid4)
    node_type: Literal[NodeType.TENSION] = NodeType.TENSION
    description: str = Field(..., description="Descripción de la tensión o contradicción.")
    node_ids: conlist(UUID4, min_length=2) = Field(..., description="IDs de los nodos que están en tensión.")


class DDIArtifact(BaseModel):
    """
    Artefacto de "Duda, Decisión, Incertidumbre" (DDI).
    Representa el estado agregado del análisis en un momento dado, consolidando
    los síntomas, hipótesis y tensiones.
    """
    artifact_id: UUID4 = Field(default_factory=uuid.uuid4)
    pyme_id: UUID4
    symptoms: list[SymptomNode] = Field(default_factory=list)
    hypotheses: list[HypothesisNode] = Field(default_factory=list)
    facts: list[FactNode] = Field(default_factory=list)
    tensions: list[TensionNode] = Field(default_factory=list)


class AdmissionState(BaseModel):
    """
    Define el estado epistemológico del caso de admisión.
    Indica qué tan cerca está el sistema de tener un entendimiento
    claro para poder actuar.
    """
    state: Literal[
        "new",
        "symptoms_captured",
        "hypotheses_generated",
        "evidence_required",
        "tensions_found",
        "ready_for_diagnosis"
    ] = Field("new", description="El estado actual del proceso de admisión.")
    pyme_id: UUID4
    details: str = Field(..., description="Descripción detallada del estado actual y próximos pasos.")

