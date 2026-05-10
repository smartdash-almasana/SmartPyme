"""
Repositorio soberano de evidencia curada BEM.

Persistencia local SQLite usando sqlite3 estándar.
Sin async. Sin ORM. Sin side effects. Fail-closed.
Tenant isolation obligatorio.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.contracts.bem_payloads import (
    BemConfidenceScore,
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS curated_evidence (
    tenant_id     TEXT NOT NULL,
    evidence_id   TEXT NOT NULL,
    kind          TEXT NOT NULL,
    payload_json  TEXT NOT NULL,
    source_json   TEXT NOT NULL,
    confidence_json TEXT,
    received_at   TEXT NOT NULL,
    trace_id      TEXT,
    PRIMARY KEY (tenant_id, evidence_id)
)
"""


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _serialize_source(source: BemSourceMetadata) -> str:
    return json.dumps(
        {
            "source_name": source.source_name,
            "source_type": source.source_type,
            "uploaded_at": source.uploaded_at,
            "external_reference_id": source.external_reference_id,
        },
        ensure_ascii=False,
    )


def _deserialize_source(raw: str) -> BemSourceMetadata:
    data: dict[str, Any] = json.loads(raw)
    return BemSourceMetadata(
        source_name=data["source_name"],
        source_type=data["source_type"],
        uploaded_at=data.get("uploaded_at"),
        external_reference_id=data.get("external_reference_id"),
    )


def _serialize_confidence(confidence: BemConfidenceScore | None) -> str | None:
    if confidence is None:
        return None
    return json.dumps(
        {"score": confidence.score, "provider": confidence.provider},
        ensure_ascii=False,
    )


def _deserialize_confidence(raw: str | None) -> BemConfidenceScore | None:
    if raw is None:
        return None
    data: dict[str, Any] = json.loads(raw)
    return BemConfidenceScore(score=data["score"], provider=data.get("provider"))


def _row_to_record(row: tuple[Any, ...]) -> CuratedEvidenceRecord:
    (
        tenant_id,
        evidence_id,
        kind_str,
        payload_json,
        source_json,
        confidence_json,
        received_at,
        trace_id,
    ) = row
    return CuratedEvidenceRecord(
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        kind=EvidenceKind(kind_str),
        payload=json.loads(payload_json),
        source_metadata=_deserialize_source(source_json),
        received_at=received_at,
        confidence=_deserialize_confidence(confidence_json),
        trace_id=trace_id,
    )


class CuratedEvidenceRepositoryBackend:
    """
    Repositorio SQLite local para evidencia curada BEM.

    Parámetros
    ----------
    db_path:
        Ruta al archivo SQLite. Puede ser ``:memory:`` para tests.
    """

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._init_schema()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE_SQL)
            conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(self, evidence: CuratedEvidenceRecord) -> None:
        """
        Persiste un registro de evidencia curada.

        Falla si tenant_id o evidence_id están vacíos.
        Falla con IntegrityError si el par (tenant_id, evidence_id) ya existe.
        """
        _require_non_empty(evidence.tenant_id, "tenant_id")
        _require_non_empty(evidence.evidence_id, "evidence_id")

        payload_json = json.dumps(evidence.payload, ensure_ascii=False)
        source_json = _serialize_source(evidence.source_metadata)
        confidence_json = _serialize_confidence(evidence.confidence)

        sql = """
            INSERT INTO curated_evidence
                (tenant_id, evidence_id, kind, payload_json, source_json,
                 confidence_json, received_at, trace_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(
                sql,
                (
                    evidence.tenant_id,
                    evidence.evidence_id,
                    evidence.kind.value,
                    payload_json,
                    source_json,
                    confidence_json,
                    evidence.received_at,
                    evidence.trace_id,
                ),
            )
            conn.commit()

    def get_by_evidence_id(
        self,
        tenant_id: str,
        evidence_id: str,
    ) -> CuratedEvidenceRecord | None:
        """
        Retorna el registro para (tenant_id, evidence_id) o None si no existe.

        Tenant isolation: solo retorna registros del tenant indicado.
        """
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(evidence_id, "evidence_id")

        sql = """
            SELECT tenant_id, evidence_id, kind, payload_json, source_json,
                   confidence_json, received_at, trace_id
            FROM curated_evidence
            WHERE tenant_id = ? AND evidence_id = ?
        """
        with self._connect() as conn:
            cursor = conn.execute(sql, (tenant_id, evidence_id))
            row = cursor.fetchone()

        if row is None:
            return None
        return _row_to_record(row)

    def list_by_tenant(self, tenant_id: str) -> list[CuratedEvidenceRecord]:
        """
        Retorna todos los registros del tenant indicado.

        Tenant isolation: nunca retorna registros de otros tenants.
        """
        _require_non_empty(tenant_id, "tenant_id")

        sql = """
            SELECT tenant_id, evidence_id, kind, payload_json, source_json,
                   confidence_json, received_at, trace_id
            FROM curated_evidence
            WHERE tenant_id = ?
            ORDER BY received_at ASC
        """
        with self._connect() as conn:
            cursor = conn.execute(sql, (tenant_id,))
            rows = cursor.fetchall()

        return [_row_to_record(row) for row in rows]
