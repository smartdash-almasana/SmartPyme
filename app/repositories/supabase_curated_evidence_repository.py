"""Adapter Supabase para CuratedEvidenceRecord — SmartPyme.

Implementa una interfaz compatible con CuratedEvidenceRepositoryBackend:
    - create(record) [upsert por tenant_id+evidence_id]
    - save(record)   [alias de create]
    - get_by_evidence_id(tenant_id, evidence_id)
    - list_by_tenant(tenant_id)

Reglas:
    - tenant_id obligatorio (fail-closed).
    - Todas las lecturas filtran por tenant_id.
    - Aislamiento multi-tenant obligatorio.
    - Sin red en tests (cliente inyectado fake).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.contracts.bem_payloads import BemSourceMetadata, CuratedEvidenceRecord, EvidenceKind
from app.repositories.persistence_provider import validate_supabase_env

_TABLE = "curated_evidence"


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _parse_received_at(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        raise ValueError("received_at inválido: debe ser ISO-8601") from exc


class SupabaseCuratedEvidenceRepository:
    """Adapter Supabase para CuratedEvidenceRecord."""

    def __init__(self, supabase_client: Any | None = None) -> None:
        if supabase_client is None:
            validate_supabase_env()
            self._client = self._build_real_client()
        else:
            self._client = supabase_client

    def create(self, evidence: CuratedEvidenceRecord) -> None:
        _require_non_empty(evidence.tenant_id, "tenant_id")
        _require_non_empty(evidence.evidence_id, "evidence_id")
        _parse_received_at(evidence.received_at)

        row: dict[str, Any] = {
            "tenant_id": evidence.tenant_id,
            "evidence_id": evidence.evidence_id,
            "kind": evidence.kind.value,
            "payload": dict(evidence.payload),
            "source_metadata": {
                "source_name": evidence.source_metadata.source_name,
                "source_type": evidence.source_metadata.source_type,
                "uploaded_at": evidence.source_metadata.uploaded_at,
                "external_reference_id": evidence.source_metadata.external_reference_id,
            },
            "received_at": evidence.received_at,
        }
        (
            self._client
            .table(_TABLE)
            .upsert(row, on_conflict="tenant_id,evidence_id")
            .execute()
        )

    def save(self, evidence: CuratedEvidenceRecord) -> None:
        self.create(evidence)

    def get_by_evidence_id(self, tenant_id: str, evidence_id: str) -> CuratedEvidenceRecord | None:
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(evidence_id, "evidence_id")

        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("evidence_id", evidence_id)
            .execute()
        )
        rows = response.data
        if not rows:
            return None
        return self._row_to_record(rows[0], expected_tenant_id=tenant_id)

    def list_by_tenant(self, tenant_id: str) -> list[CuratedEvidenceRecord]:
        _require_non_empty(tenant_id, "tenant_id")

        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("tenant_id", tenant_id)
            .execute()
        )
        rows = response.data
        records = [self._row_to_record(row, expected_tenant_id=tenant_id) for row in rows]
        records.sort(key=lambda r: r.received_at)
        return records

    @staticmethod
    def _row_to_record(row: dict[str, Any], expected_tenant_id: str) -> CuratedEvidenceRecord:
        tenant_id = row.get("tenant_id", "")
        if tenant_id != expected_tenant_id:
            raise ValueError(
                f"tenant_id mismatch en lectura: esperado={expected_tenant_id!r}, recibido={tenant_id!r}"
            )

        source_raw = row.get("source_metadata") or {}
        if not isinstance(source_raw, dict):
            raise ValueError("source_metadata inválido en fila Supabase")

        return CuratedEvidenceRecord(
            tenant_id=tenant_id,
            evidence_id=row["evidence_id"],
            kind=EvidenceKind(str(row["kind"]).lower()),
            payload=dict(row.get("payload") or {}),
            source_metadata=BemSourceMetadata(
                source_name=source_raw.get("source_name", ""),
                source_type=source_raw.get("source_type", ""),
                uploaded_at=source_raw.get("uploaded_at"),
                external_reference_id=source_raw.get("external_reference_id"),
            ),
            received_at=row["received_at"],
            confidence=None,
            trace_id=None,
        )

    @staticmethod
    def _build_real_client() -> Any:
        import os

        try:
            from supabase import create_client  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "BLOCKED_MISSING_DEPENDENCY: la librería 'supabase' no está instalada. "
                "Instalar con: pip install supabase"
            ) from exc

        url = os.environ["SMARTPYME_SUPABASE_URL"]
        key = os.environ["SMARTPYME_SUPABASE_KEY"]
        return create_client(url, key)
