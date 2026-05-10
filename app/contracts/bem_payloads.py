"""
Contratos soberanos para recibir payloads curados desde BEM.

BEM es la capa externa de ingestión y curado documental.
SmartPyme recibe evidencia ya curada y estructurada (ADR-004).

Sin Pydantic. Sin side effects. Fail-closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Helpers de validación
# ---------------------------------------------------------------------------


def _require_non_empty(value: str, field_name: str) -> None:
    """Falla si el valor es vacío o solo espacios."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _require_non_empty_dict(value: dict[str, Any], field_name: str) -> None:
    """Falla si el dict es None o vacío."""
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _validate_confidence_score(score: float, field_name: str = "score") -> None:
    """Falla si el score está fuera del rango [0.0, 1.0]."""
    if not isinstance(score, (int, float)):
        raise TypeError(f"{field_name} debe ser un número")
    if not (0.0 <= float(score) <= 1.0):
        raise ValueError(f"{field_name} debe estar entre 0.0 y 1.0, recibido: {score}")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class EvidenceKind(str, Enum):
    """Tipo de evidencia curada recibida desde BEM."""

    EXCEL = "excel"
    PDF = "pdf"
    IMAGE = "image"
    EMAIL = "email"
    AUDIO = "audio"
    MIXED = "mixed"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class BemSourceMetadata:
    """Metadata sobre el origen del documento procesado por BEM."""

    source_name: str
    source_type: str
    uploaded_at: str | None = None
    external_reference_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.source_name, "source_name")
        _require_non_empty(self.source_type, "source_type")
        if self.uploaded_at is not None and not isinstance(self.uploaded_at, str):
            raise TypeError("uploaded_at debe ser str o None")
        if self.external_reference_id is not None and not isinstance(
            self.external_reference_id, str
        ):
            raise TypeError("external_reference_id debe ser str o None")


@dataclass(slots=True)
class BemConfidenceScore:
    """Puntuación de confianza reportada por BEM sobre la evidencia curada."""

    score: float
    provider: str | None = None

    def __post_init__(self) -> None:
        _validate_confidence_score(self.score, "score")
        if self.provider is not None and not isinstance(self.provider, str):
            raise TypeError("provider debe ser str o None")


@dataclass(slots=True)
class CuratedEvidenceRecord:
    """
    Registro de evidencia curada recibida desde BEM.

    Representa el contrato soberano de SmartPyme para ingerir
    evidencia ya procesada por la capa externa de curado documental.
    """

    tenant_id: str
    evidence_id: str
    kind: EvidenceKind
    payload: dict[str, Any]
    source_metadata: BemSourceMetadata
    received_at: str
    confidence: BemConfidenceScore | None = None
    trace_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.tenant_id, "tenant_id")
        _require_non_empty(self.evidence_id, "evidence_id")
        _require_non_empty_dict(self.payload, "payload")
        _require_non_empty(self.received_at, "received_at")

        if not isinstance(self.kind, EvidenceKind):
            raise TypeError("kind debe ser EvidenceKind")
        if not isinstance(self.source_metadata, BemSourceMetadata):
            raise TypeError("source_metadata debe ser BemSourceMetadata")
        if self.confidence is not None and not isinstance(self.confidence, BemConfidenceScore):
            raise TypeError("confidence debe ser BemConfidenceScore o None")
        if self.trace_id is not None and not isinstance(self.trace_id, str):
            raise TypeError("trace_id debe ser str o None")
