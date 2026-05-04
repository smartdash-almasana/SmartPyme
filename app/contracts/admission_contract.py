"""
Contratos Pydantic — Capa 1: Admisión Epistemológica
TS_ADM_001_CONTRATOS_ADMISION

Modelos de datos mínimos para representar InitialCaseAdmission y sus objetos
componentes. Sin lógica de servicio, sin diagnóstico, sin OperationalCase.

Documento rector: docs/product/SMARTPYME_CAPA_01_ADMISION_EPISTEMOLOGICA.md
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumeraciones literales
# ---------------------------------------------------------------------------

EpistemicState = Literal["CERTEZA", "DUDA", "DESCONOCIMIENTO"]
"""
Estado epistemológico de un bloque de información.

CERTEZA       → dato disponible o afirmado como existente; permite avanzar.
DUDA          → podría existir pero no está confirmado; genera tarea.
DESCONOCIMIENTO → inexistente o inaccesible; se excluye salvo ROI suficiente.
"""

ClinicalPhase = Literal["SANGRIA", "INESTABILIDAD", "OPTIMIZACION"]
"""
Fase clínica del problema detectado en la admisión.

SANGRIA       → pérdida económica activa o sospecha fuerte. Prioridad máxima.
INESTABILIDAD → desorden operativo que impide controlar el negocio.
OPTIMIZACION  → negocio funciona; busca mejorar.
"""

EvidenceAvailability = Literal["NOW", "SCHEDULED", "UNKNOWN"]
"""
Disponibilidad temporal de una evidencia.

NOW       → disponible en este momento.
SCHEDULED → existe pero no está disponible todavía; tiene fecha estimada.
UNKNOWN   → no se sabe cuándo estará disponible.
"""

TaskStatus = Literal["PENDING", "DONE", "DISCARDED"]
"""
Estado de una tarea de evidencia.

PENDING   → pendiente de ejecución (valor por defecto).
DONE      → completada.
DISCARDED → descartada por falta de ROI o cambio de alcance.
"""

Area = Literal[
    "caja",
    "stock",
    "ventas",
    "admin",
    "produccion",
    "mixto",
]
"""
Área operativa principal de la demanda del dueño.
"""


# ---------------------------------------------------------------------------
# Modelos de personas y fuentes
# ---------------------------------------------------------------------------


class Person(BaseModel):
    """
    Persona identificada en la conversación como nodo de acceso a información.
    """

    person_id: str = Field(..., description="Identificador único de la persona en el caso.")
    name: str = Field(..., description="Nombre o apodo con el que el dueño la menciona.")
    role: str = Field(..., description="Rol operativo: contador, encargado, Paulita, etc.")
    contact: Optional[str] = Field(default=None, description="Canal de contacto opcional.")


class Source(BaseModel):
    """
    Fuente de información identificada: Excel, PDF, WhatsApp, sistema, etc.
    """

    source_id: str = Field(..., description="Identificador único de la fuente.")
    source_type: Literal[
        "excel", "pdf", "whatsapp", "libreta", "sistema", "humano", "api", "mcp", "otro"
    ] = Field(..., description="Tipo de fuente.")
    owner_person_id: Optional[str] = Field(
        default=None, description="ID de la persona que gestiona esta fuente."
    )
    location: Optional[str] = Field(
        default=None, description="Ubicación física o lógica de la fuente."
    )
    notes: Optional[str] = Field(default=None, description="Notas adicionales.")


# ---------------------------------------------------------------------------
# Modelos de evidencia y tareas
# ---------------------------------------------------------------------------


class EvidenceItem(BaseModel):
    """
    Bloque de información con su estado epistemológico y disponibilidad temporal.
    """

    evidence_id: str = Field(..., description="Identificador único de la evidencia.")
    evidence_type: str = Field(
        ..., description="Tipo semántico: Excel_stock, reporte_gastos, etc."
    )
    format: Optional[str] = Field(default=None, description="Formato esperado: xlsx, pdf, etc.")
    source_id: Optional[str] = Field(
        default=None, description="ID de la fuente que contiene esta evidencia."
    )
    responsible_person_id: Optional[str] = Field(
        default=None, description="ID de la persona responsable de proveer esta evidencia."
    )
    epistemic_state: EpistemicState = Field(
        ..., description="Estado epistemológico: CERTEZA, DUDA o DESCONOCIMIENTO."
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza en la certeza declarada. Rango [0, 1].",
    )
    availability: EvidenceAvailability = Field(
        default="UNKNOWN",
        description="Disponibilidad temporal de la evidencia.",
    )
    earliest_date: Optional[datetime] = Field(
        default=None, description="Fecha más temprana estimada de disponibilidad."
    )
    due_date: Optional[datetime] = Field(
        default=None, description="Fecha límite para obtener la evidencia."
    )
    notes: Optional[str] = Field(default=None, description="Notas adicionales.")


class EvidenceTask(BaseModel):
    """
    Tarea generada para obtener, confirmar o descartar una evidencia en DUDA.
    """

    task_id: str = Field(..., description="Identificador único de la tarea.")
    task_type: Literal[
        "REQUEST_EVIDENCE", "FOLLOW_UP", "CONFIRM_SOURCE", "REPLAN", "DISCARD_SCOPE"
    ] = Field(..., description="Tipo de acción requerida.")
    evidence_id: str = Field(
        ..., description="ID de la evidencia a la que se refiere esta tarea."
    )
    responsible_person_id: Optional[str] = Field(
        default=None, description="ID de la persona responsable de ejecutar la tarea."
    )
    instruction: str = Field(
        ..., description="Instrucción concreta para el dueño o el sistema."
    )
    due_date: Optional[datetime] = Field(
        default=None, description="Fecha límite para completar la tarea."
    )
    status: TaskStatus = Field(
        default="PENDING",
        description="Estado de la tarea. Por defecto: PENDING.",
    )


# ---------------------------------------------------------------------------
# Modelos de demanda y candidatos semánticos
# ---------------------------------------------------------------------------


class OwnerDemand(BaseModel):
    """
    Demanda del dueño tal como fue recibida y procesada en la admisión.
    """

    raw_text: str = Field(..., description="Texto original del dueño, sin modificar.")
    explicit_objective: str = Field(
        ..., description="Objetivo explícito extraído del planteo."
    )
    inferred_objectives: list[str] = Field(
        default_factory=list,
        description="Objetivos inferidos semánticamente. No habilitan acción sin validación.",
    )
    area: Area = Field(..., description="Área operativa principal de la demanda.")
    urgency: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Urgencia percibida de la demanda. Rango [1, 5].",
    )


class SymptomCandidate(BaseModel):
    """
    Síntoma operativo candidato detectado semánticamente en la admisión.
    El síntoma no es patología confirmada.
    """

    symptom_id: str = Field(..., description="ID del síntoma en el catálogo clínico-operativo.")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en la detección del síntoma. Rango [0, 1].",
    )


class PathologyCandidate(BaseModel):
    """
    Patología operativa candidata asociada a los síntomas detectados.
    La patología posible no es hallazgo confirmado.
    """

    pathology_id: str = Field(
        ..., description="ID de la patología en el catálogo clínico-operativo."
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score de relevancia de la patología candidata. Rango [0, 1].",
    )
    reason: Optional[str] = Field(
        default=None, description="Razón semántica por la que se candidatea esta patología."
    )


# ---------------------------------------------------------------------------
# Objeto de salida de la Capa 1
# ---------------------------------------------------------------------------


class InitialCaseAdmission(BaseModel):
    """
    Output exclusivo de la Capa 1 de Admisión Epistemológica.

    Consolida el entendimiento inicial del caso: demanda, personas, fuentes,
    evidencias, tareas, fase clínica, síntomas y patologías candidatas.

    NO es un diagnóstico.
    NO es un OperationalCase.
    Su propósito es validar el punto de partida con el dueño.
    """

    case_id: str = Field(..., description="Identificador único del caso de admisión.")
    cliente_id: str = Field(..., description="Identificador del cliente / tenant.")
    demand: OwnerDemand = Field(..., description="Demanda procesada del dueño.")
    clinical_phase: ClinicalPhase = Field(
        ..., description="Fase clínica detectada: SANGRIA, INESTABILIDAD u OPTIMIZACION."
    )
    people: list[Person] = Field(
        default_factory=list,
        description="Personas identificadas como nodos de acceso a información.",
    )
    sources: list[Source] = Field(
        default_factory=list,
        description="Fuentes de información identificadas en la conversación.",
    )
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Evidencias con su estado epistemológico y disponibilidad.",
    )
    tasks: list[EvidenceTask] = Field(
        default_factory=list,
        description="Tareas pendientes para obtener o confirmar evidencia.",
    )
    symptoms: list[SymptomCandidate] = Field(
        default_factory=list,
        description="Síntomas operativos candidatos detectados semánticamente.",
    )
    pathologies: list[PathologyCandidate] = Field(
        default_factory=list,
        description="Patologías operativas candidatas asociadas a los síntomas.",
    )
    next_step: str = Field(
        ...,
        description="Próximo paso sugerido para el dueño o el sistema.",
    )
