from __future__ import annotations

import hashlib
from typing import Any

from app.contracts.clarification_contract import Clarification
from app.repositories.clarification_repository import ClarificationRepository


class ClarificationService:
    def __init__(self, repository: ClarificationRepository) -> None:
        self.repository = repository

    def create_blocking_clarification(
        self,
        question: str,
        reason: str,
        job_id: str | None = None,
        traceable_origin: dict[str, Any] | None = None,
    ) -> Clarification:
        clarification_id = _build_clarification_id(question, job_id)
        clarification = Clarification(
            clarification_id=clarification_id,
            job_id=job_id,
            question=question,
            reason=reason,
            status="pending",
            blocking=True,
            answer=None,
            traceable_origin=traceable_origin or {},
        )
        self.repository.save(clarification)
        return clarification

    def answer_clarification(
        self, clarification_id: str, answer: str
    ) -> None:
        self.repository.mark_answered(clarification_id, answer)

    def has_pending_blockers(self, job_id: str | None = None) -> bool:
        return self.repository.has_pending(job_id=job_id)


def _build_clarification_id(question: str, job_id: str | None) -> str:
    digest = hashlib.sha256(
        f"{job_id or ''}:{question}".encode()
    ).hexdigest()
    return f"clarif_{digest[:16]}"
