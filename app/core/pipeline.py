from __future__ import annotations

from app.services.fact_extraction_service import FactExtractionService
from app.services.canonicalization_service import CanonicalizationService
from app.services.entity_resolution_service import EntityResolutionService
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository


class Pipeline:
    def __init__(
        self,
        fact_repo: FactRepository,
        canonical_repo: CanonicalRepository,
        entity_repo: EntityRepository,
    ) -> None:
        self.fact_extraction_service = FactExtractionService(fact_repo)
        self.canonicalization_service = CanonicalizationService(canonical_repo)
        self.entity_resolution_service = EntityResolutionService(entity_repo)
        self.fact_repo = fact_repo

    def process_text(
        self, evidence_id: str, text: str, job_id: str | None = None, plan_id: str | None = None
    ) -> dict:
        # 1. Extract facts
        fact_extraction_result = self.fact_extraction_service.extract_from_evidence(
            evidence_id=evidence_id, text=text, job_id=job_id, plan_id=plan_id
        )

        # 2. Get the extracted facts
        facts = self.fact_repo.list_facts(evidence_id=evidence_id)

        # 3. Canonicalize facts
        canonicalization_result = self.canonicalization_service.canonicalize_facts(
            facts=facts, job_id=job_id, plan_id=plan_id
        )

        # 4. Get the canonical rows
        canonical_rows = self.canonicalization_service.repository.list_canonical_rows(evidence_id=evidence_id)

        # 5. Resolve entities
        entity_resolution_result = self.entity_resolution_service.resolve_entities(
            canonical_rows=canonical_rows, job_id=job_id, plan_id=plan_id
        )

        return {
            "fact_extraction": fact_extraction_result,
            "canonicalization": canonicalization_result,
            "entity_resolution": entity_resolution_result,
        }
