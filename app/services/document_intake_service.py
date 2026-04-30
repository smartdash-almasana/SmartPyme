from __future__ import annotations

from pathlib import Path
from typing import Any

from app.contracts.bem_evidence_contract import (
    BemDocumentType,
    BemEvidenceCandidate,
    BemEvidenceStatus,
)
from app.repositories.evidence_candidate_repository import EvidenceCandidateRepository


DEFAULT_EVIDENCE_CANDIDATES_DB = Path("data/evidence_candidates.db")
DOCUMENT_TYPE_BY_EXTENSION: dict[str, BemDocumentType] = {
    ".pdf": BemDocumentType.UNKNOWN,
    ".xlsx": BemDocumentType.UNKNOWN,
    ".csv": BemDocumentType.UNKNOWN,
}


class DocumentIntakeService:
    def __init__(self, db_path: str | Path = DEFAULT_EVIDENCE_CANDIDATES_DB) -> None:
        self.db_path = Path(db_path)

    def register_telegram_document_candidate(
        self,
        *,
        cliente_id: str,
        telegram_user_id: str | int,
        file_id: str | None,
        file_name: str,
        mime_type: str | None = None,
    ) -> BemEvidenceCandidate:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required")
        if not file_name or not file_name.strip():
            raise ValueError("file_name is required")

        extension = Path(file_name).suffix.lower()
        document_type = DOCUMENT_TYPE_BY_EXTENSION.get(extension, BemDocumentType.UNKNOWN)
        source_evidence_id = f"telegram:{cliente_id}:{file_id or file_name}"
        segment_id = "document"
        evidence_id = f"{source_evidence_id}:{segment_id}"
        storage_ref = f"telegram_file:{file_id}" if file_id else None
        source_ref = f"telegram:{telegram_user_id}:document:{file_id or file_name}"
        metadata: dict[str, Any] = {
            "origin": "telegram",
            "telegram_user_id": str(telegram_user_id),
            "file_id": file_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "extension": extension,
            "truth_status": "candidate_not_fact",
            "bem_real_used": False,
        }

        candidate = BemEvidenceCandidate(
            cliente_id=cliente_id,
            evidence_id=evidence_id,
            source_evidence_id=source_evidence_id,
            segment_id=segment_id,
            document_type=document_type,
            status=BemEvidenceStatus.CANDIDATE,
            storage_ref=storage_ref,
            source_refs=[source_ref],
            confidence=None,
            bem_call_id=None,
            workflow_name="telegram_document_intake_stub",
            workflow_version="ts_016",
            metadata=metadata,
        )

        EvidenceCandidateRepository(cliente_id, self.db_path).save(candidate)
        return candidate
