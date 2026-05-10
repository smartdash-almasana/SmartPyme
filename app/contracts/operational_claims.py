from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


class ClaimType(str, Enum):
    DEUDA_COBRANZA = "deuda_cobranza"
    STOCK = "stock"
    VENTAS = "ventas"
    COSTOS = "costos"
    MARGEN = "margen"
    PROVEEDOR = "proveedor"
    CLIENTE = "cliente"
    FACTURACION = "facturacion"


class ClaimEstado(str, Enum):
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EVIDENCE_REQUESTED = "evidence_requested"
    EVIDENCE_RECEIVED = "evidence_received"
    SUPPORTED = "supported"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ClaimCatalogEntry:
    significado_operacional: str
    datos_minimos: tuple[str, ...]
    evidencia_esperada: tuple[str, ...]
    pregunta_confirmacion: str
    pregunta_evidencia: str
    prioridad_revision: str
    riesgo_si_es_falso: str

    def __post_init__(self) -> None:
        _require_non_empty(self.significado_operacional, "significado_operacional")
        _require_non_empty(self.pregunta_confirmacion, "pregunta_confirmacion")
        _require_non_empty(self.pregunta_evidencia, "pregunta_evidencia")
        _require_non_empty(self.prioridad_revision, "prioridad_revision")
        _require_non_empty(self.riesgo_si_es_falso, "riesgo_si_es_falso")
        if len(self.datos_minimos) < 2:
            raise ValueError("datos_minimos must contain at least two items")
        if len(self.evidencia_esperada) < 2:
            raise ValueError("evidencia_esperada must contain at least two items")


@dataclass(frozen=True, slots=True)
class OperationalClaim:
    tenant_id: str
    session_id: str
    source_turn_id: str
    claim_type: ClaimType
    statement: str
    status: ClaimEstado = ClaimEstado.PENDING_CONFIRMATION
    claim_id: str = field(default_factory=lambda: str(uuid4()))
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    creado_en: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self) -> None:
        _require_non_empty(self.tenant_id, "tenant_id")
        _require_non_empty(self.session_id, "session_id")
        _require_non_empty(self.source_turn_id, "source_turn_id")
        _require_non_empty(self.statement, "statement")
        if not isinstance(self.claim_type, ClaimType):
            raise TypeError("claim_type must be ClaimType")
        if not isinstance(self.status, ClaimEstado):
            raise TypeError("status must be ClaimEstado")

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "source_turn_id": self.source_turn_id,
            "claim_type": self.claim_type.value,
            "statement": self.statement,
            "status": self.status.value,
            "claim_id": self.claim_id,
            "evidence_ids": list(self.evidence_ids),
            "metadata": dict(self.metadata),
            "creado_en": self.creado_en,
        }


CLAIM_CATALOG: dict[ClaimType, ClaimCatalogEntry] = {
    claim_type: ClaimCatalogEntry(
        significado_operacional=f"Claim operacional de tipo {claim_type.value}.",
        datos_minimos=("entidad", "valor_o_descripcion"),
        evidencia_esperada=("documento", "registro_operacional"),
        pregunta_confirmacion=f"¿Confirmás que el problema corresponde a {claim_type.value}?",
        pregunta_evidencia="¿Podés aportar documento, registro o comprobante relacionado?",
        prioridad_revision="alta" if claim_type in {ClaimType.DEUDA_COBRANZA, ClaimType.STOCK, ClaimType.COSTOS, ClaimType.MARGEN, ClaimType.FACTURACION} else "media",
        riesgo_si_es_falso="Puede generar un diagnóstico operacional incorrecto.",
    )
    for claim_type in ClaimType
}


_ALLOWED_TRANSITIONS: set[tuple[ClaimEstado, ClaimEstado]] = {
    (ClaimEstado.PENDING_CONFIRMATION, ClaimEstado.CONFIRMED),
    (ClaimEstado.PENDING_CONFIRMATION, ClaimEstado.REJECTED),
    (ClaimEstado.PENDING_CONFIRMATION, ClaimEstado.BLOCKED),
    (ClaimEstado.CONFIRMED, ClaimEstado.EVIDENCE_REQUESTED),
    (ClaimEstado.CONFIRMED, ClaimEstado.BLOCKED),
    (ClaimEstado.EVIDENCE_REQUESTED, ClaimEstado.EVIDENCE_RECEIVED),
    (ClaimEstado.EVIDENCE_REQUESTED, ClaimEstado.BLOCKED),
    (ClaimEstado.EVIDENCE_RECEIVED, ClaimEstado.SUPPORTED),
    (ClaimEstado.EVIDENCE_RECEIVED, ClaimEstado.BLOCKED),
    (ClaimEstado.REJECTED, ClaimEstado.BLOCKED),
}


def transicion_valida(actual: ClaimEstado, siguiente: ClaimEstado) -> bool:
    if not isinstance(actual, ClaimEstado):
        raise TypeError("actual must be ClaimEstado")
    if not isinstance(siguiente, ClaimEstado):
        raise TypeError("siguiente must be ClaimEstado")
    return (actual, siguiente) in _ALLOWED_TRANSITIONS


def resolver_estado_fail_closed(actual: ClaimEstado, siguiente: ClaimEstado) -> ClaimEstado:
    return siguiente if transicion_valida(actual, siguiente) else ClaimEstado.BLOCKED


def puede_marcar_supported(claim: OperationalClaim) -> bool:
    if not isinstance(claim, OperationalClaim):
        raise TypeError("claim must be OperationalClaim")
    return claim.status == ClaimEstado.EVIDENCE_RECEIVED and bool(claim.evidence_ids)


def claims_del_tenant(claims: list[OperationalClaim], tenant_id: str) -> list[OperationalClaim]:
    _require_non_empty(tenant_id, "tenant_id")
    return [claim for claim in claims if claim.tenant_id == tenant_id]
