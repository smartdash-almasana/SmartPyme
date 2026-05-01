from __future__ import annotations

import hashlib
from typing import Any

from app.contracts.evidence_contract import CanonicalRowCandidate, ExtractedFactCandidate
from app.repositories.canonical_repository import CanonicalRepository


class CanonicalizationService:
    def __init__(self, repository: CanonicalRepository) -> None:
        self.repository = repository

    def canonicalize_facts(
        self,
        facts: list[ExtractedFactCandidate],
        job_id: str | None = None,
        plan_id: str | None = None,
    ) -> dict[str, Any]:
        canonical_rows = self._create_canonical_rows(facts, job_id=job_id, plan_id=plan_id)
        self.repository.save_batch(canonical_rows)
        return {
            "status": "CANONICALIZED",
            "job_id": job_id,
            "plan_id": plan_id,
            "canonical_rows_count": len(canonical_rows),
            "canonical_row_ids": [row.canonical_row_id for row in canonical_rows],
        }

    def _create_canonical_rows(
        self,
        facts: list[ExtractedFactCandidate],
        job_id: str | None = None,
        plan_id: str | None = None,
    ) -> list[CanonicalRowCandidate]:
        return [
            self._create_canonical_row(fact, job_id=job_id, plan_id=plan_id) for fact in facts
        ]

    def _create_canonical_row(
        self, fact: ExtractedFactCandidate, job_id: str | None = None, plan_id: str | None = None
    ) -> CanonicalRowCandidate:
        entity_type = fact.schema_name.replace("simple_", "")
        canonical_row_id = _build_canonical_id(fact.fact_candidate_id, entity_type)
        return CanonicalRowCandidate(
            cliente_id=fact.cliente_id,
            canonical_row_id=canonical_row_id,
            fact_candidate_id=fact.fact_candidate_id,
            evidence_id=fact.evidence_id,
            job_id=job_id or fact.job_id,
            plan_id=plan_id or fact.plan_id,
            entity_type=entity_type,
            row=fact.data,
            validation_status="pending_validation",
            errors=[]
        )


def _build_canonical_id(fact_candidate_id: str, entity_type: str) -> str:
    digest = hashlib.sha256(f"{fact_candidate_id}:{entity_type}".encode()).hexdigest()
    return f"canonical_{digest[:16]}"
