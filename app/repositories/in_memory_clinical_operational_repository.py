"""Repositorio in-memory para persistencia táctica clínico-operacional.

Responsabilidad:
    Persistencia táctica in-memory para tests y futura orquestación.

Regla rectora:
    IA interpreta. Determinístico decide. Evidencia gobierna. Dueño confirma.

Este repositorio:
    - NO diagnostica.
    - NO clasifica.
    - NO calcula.
    - NO emite hallazgos.
    - NO decide por el dueño.

Garantías:
    - Aislamiento soberano por tenant_id: un tenant nunca lee registros de otro.
    - Fail-closed: tenant_id, reception_id o evidence_id vacíos lanzan ValueError.
    - Upsert por (tenant_id, id): save pisa el registro previo del mismo par.
    - Sin DB, sin red, sin dependencias externas.
"""

from __future__ import annotations

from app.contracts.clinical_operational_contracts import (
    EvidenceRecord,
    ReceptionRecord,
)


def _require_non_empty(value: str, field_name: str) -> None:
    """Fail-closed: rechaza strings vacíos o solo espacios."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} no puede ser vacío: {value!r}")


class InMemoryClinicalOperationalRepository:
    """Repositorio in-memory para ReceptionRecord y EvidenceRecord.

    Almacena registros en dicts indexados por (tenant_id, id).
    Cada operación valida tenant_id antes de tocar el store.
    """

    def __init__(self) -> None:
        # dict[(tenant_id, reception_id), ReceptionRecord]
        self._receptions: dict[tuple[str, str], ReceptionRecord] = {}
        # dict[(tenant_id, evidence_id), EvidenceRecord]
        self._evidence: dict[tuple[str, str], EvidenceRecord] = {}

    # ------------------------------------------------------------------
    # ReceptionRecord
    # ------------------------------------------------------------------

    def save_reception(self, record: ReceptionRecord) -> ReceptionRecord:
        """Persiste o actualiza un ReceptionRecord (upsert por tenant+id).

        El contrato Pydantic ya valida tenant_id y reception_id no vacíos.
        El repositorio valida adicionalmente para fail-closed explícito.
        """
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.reception_id, "reception_id")
        key = (record.tenant_id, record.reception_id)
        self._receptions[key] = record
        return record

    def get_reception(
        self, tenant_id: str, reception_id: str
    ) -> ReceptionRecord | None:
        """Devuelve el ReceptionRecord del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(reception_id, "reception_id")
        return self._receptions.get((tenant_id, reception_id))

    def list_receptions(self, tenant_id: str) -> list[ReceptionRecord]:
        """Devuelve todos los ReceptionRecord del tenant, en orden de inserción."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._receptions.items()
            if tid == tenant_id
        ]

    # ------------------------------------------------------------------
    # EvidenceRecord
    # ------------------------------------------------------------------

    def save_evidence(self, record: EvidenceRecord) -> EvidenceRecord:
        """Persiste o actualiza un EvidenceRecord (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.evidence_id, "evidence_id")
        key = (record.tenant_id, record.evidence_id)
        self._evidence[key] = record
        return record

    def get_evidence(
        self, tenant_id: str, evidence_id: str
    ) -> EvidenceRecord | None:
        """Devuelve el EvidenceRecord del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(evidence_id, "evidence_id")
        return self._evidence.get((tenant_id, evidence_id))

    def list_evidence(self, tenant_id: str) -> list[EvidenceRecord]:
        """Devuelve todos los EvidenceRecord del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._evidence.items()
            if tid == tenant_id
        ]

    def list_evidence_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[EvidenceRecord]:
        """Devuelve EvidenceRecord del tenant vinculados a una reception."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(reception_id, "reception_id")
        return [
            record
            for (tid, _), record in self._evidence.items()
            if tid == tenant_id and record.linked_reception_id == reception_id
        ]
