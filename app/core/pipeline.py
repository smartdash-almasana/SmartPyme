from __future__ import annotations

from app.services.fact_extraction_service import FactExtractionService
from app.services.canonicalization_service import CanonicalizationService
from app.services.entity_resolution_service import EntityResolutionService
from app.services.comparison_service import ComparisonService
from app.services.findings_service import FindingsService
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository
from app.contracts.pipeline_contract import PipelineCounts, PipelineResult


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
        self.comparison_service = ComparisonService()
        self.findings_service = FindingsService()
        self.fact_repo = fact_repo
        self.canonical_repo = canonical_repo
        self.entity_repo = entity_repo

    def _process_one_text(
        self,
        evidence_id: str,
        text: str,
        job_id: str | None = None,
        plan_id: str | None = None,
    ) -> None:
        self.fact_extraction_service.extract_from_evidence(
            evidence_id=evidence_id, text=text, job_id=job_id, plan_id=plan_id
        )
        facts = self.fact_repo.list_facts(evidence_id=evidence_id)
        self.canonicalization_service.canonicalize_facts(facts=facts, job_id=job_id, plan_id=plan_id)
        canonical_rows = self.canonical_repo.list_canonical_rows(evidence_id=evidence_id)
        self.entity_resolution_service.resolve_entities(
            canonical_rows=canonical_rows, job_id=job_id, plan_id=plan_id
        )

    def process_texts(
        self,
        evidence_id_a: str,
        text_a: str,
        evidence_id_b: str,
        text_b: str,
        job_id: str | None = None,
        plan_id: str | None = None,
    ) -> PipelineResult:
        errors: list[str] = []

        self._process_one_text(evidence_id_a, text_a, job_id, plan_id)
        self._process_one_text(evidence_id_b, text_b, job_id, plan_id)

        facts = (
            self.fact_repo.list_facts(evidence_id=evidence_id_a)
            + self.fact_repo.list_facts(evidence_id=evidence_id_b)
        )
        canonical = (
            self.canonical_repo.list_canonical_rows(evidence_id=evidence_id_a)
            + self.canonical_repo.list_canonical_rows(evidence_id=evidence_id_b)
        )
        entities = self.entity_repo.list_entities()
        validated_entities = [e for e in entities if e.validation_status == "validated"]

        comparison_results = self.comparison_service.compare_entities(validated_entities)
        findings = self.findings_service.generate_findings(comparison_results)

        counts = PipelineCounts(
            facts=len(facts),
            canonical=len(canonical),
            entities=len(entities),
            validated_entities=len(validated_entities),
            comparison=len(comparison_results),
            findings=len(findings),
        )

        return PipelineResult(
            status="OK" if not errors else "ERROR",
            job_id=job_id,
            plan_id=plan_id,
            facts=facts,
            canonical=canonical,
            entities=entities,
            comparison=comparison_results,
            findings=findings,
            counts=counts,
            errors=errors,
        )
