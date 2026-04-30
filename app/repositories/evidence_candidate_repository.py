from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.contracts.bem_evidence_contract import (
    BemDocumentType,
    BemEvidenceCandidate,
    BemEvidenceStatus,
)


class EvidenceCandidateRepository:
    def __init__(self, cliente_id: str, db_path: str | Path) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required for EvidenceCandidateRepository")

        self.cliente_id = cliente_id
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_candidates (
                    cliente_id TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    source_evidence_id TEXT NOT NULL,
                    segment_id TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    storage_ref TEXT,
                    source_refs_json TEXT NOT NULL,
                    confidence REAL,
                    bem_call_id TEXT,
                    workflow_name TEXT,
                    workflow_version TEXT,
                    metadata_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (cliente_id, evidence_id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_evidence_candidates_cliente_status
                ON evidence_candidates(cliente_id, status)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_evidence_candidates_cliente_document_type
                ON evidence_candidates(cliente_id, document_type)
                """
            )

    def save(self, candidate: BemEvidenceCandidate) -> None:
        if candidate.cliente_id != self.cliente_id:
            raise ValueError("cliente_id mismatch")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO evidence_candidates (
                    cliente_id,
                    evidence_id,
                    source_evidence_id,
                    segment_id,
                    document_type,
                    status,
                    storage_ref,
                    source_refs_json,
                    confidence,
                    bem_call_id,
                    workflow_name,
                    workflow_version,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cliente_id, evidence_id) DO UPDATE SET
                    source_evidence_id = excluded.source_evidence_id,
                    segment_id = excluded.segment_id,
                    document_type = excluded.document_type,
                    status = excluded.status,
                    storage_ref = excluded.storage_ref,
                    source_refs_json = excluded.source_refs_json,
                    confidence = excluded.confidence,
                    bem_call_id = excluded.bem_call_id,
                    workflow_name = excluded.workflow_name,
                    workflow_version = excluded.workflow_version,
                    metadata_json = excluded.metadata_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    self.cliente_id,
                    candidate.evidence_id,
                    candidate.source_evidence_id,
                    candidate.segment_id,
                    candidate.document_type.value,
                    candidate.status.value,
                    candidate.storage_ref,
                    json.dumps(candidate.source_refs, ensure_ascii=False),
                    candidate.confidence,
                    candidate.bem_call_id,
                    candidate.workflow_name,
                    candidate.workflow_version,
                    json.dumps(candidate.metadata, ensure_ascii=False),
                ),
            )

    def get(self, evidence_id: str) -> BemEvidenceCandidate | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT * FROM evidence_candidates
                WHERE cliente_id = ? AND evidence_id = ?
                """,
                (self.cliente_id, evidence_id),
            ).fetchone()

        if row is None:
            return None
        return _row_to_candidate(row)

    def list_candidates(
        self,
        status: BemEvidenceStatus | str | None = None,
        document_type: BemDocumentType | str | None = None,
    ) -> list[BemEvidenceCandidate]:
        status_value = status.value if isinstance(status, BemEvidenceStatus) else status
        document_type_value = (
            document_type.value if isinstance(document_type, BemDocumentType) else document_type
        )
        query = """
            SELECT * FROM evidence_candidates
            WHERE cliente_id = ?
              AND (? IS NULL OR status = ?)
              AND (? IS NULL OR document_type = ?)
            ORDER BY created_at DESC
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                query,
                (
                    self.cliente_id,
                    status_value,
                    status_value,
                    document_type_value,
                    document_type_value,
                ),
            ).fetchall()
        return [_row_to_candidate(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_candidate(row: sqlite3.Row) -> BemEvidenceCandidate:
    return BemEvidenceCandidate(
        cliente_id=row["cliente_id"],
        evidence_id=row["evidence_id"],
        source_evidence_id=row["source_evidence_id"],
        segment_id=row["segment_id"],
        document_type=BemDocumentType(row["document_type"]),
        status=BemEvidenceStatus(row["status"]),
        storage_ref=row["storage_ref"],
        source_refs=json.loads(row["source_refs_json"]),
        confidence=row["confidence"],
        bem_call_id=row["bem_call_id"],
        workflow_name=row["workflow_name"],
        workflow_version=row["workflow_version"],
        metadata=json.loads(row["metadata_json"]),
    )
