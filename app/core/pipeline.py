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

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.repositories.finding_repository import FindingRepository
    from app.services.finding_communication_service import FindingCommunicationService
    from app.services.clarification_service import ClarificationService
    from app.services.action_proposal_service import ActionProposalService

_BLOCKED_COUNTS = PipelineCounts(
    facts=0, canonical=0, entities=0, validated_entities=0,
    comparison=0, findings=0, messages=0, action_proposals=0,
)


class Pipeline:
    def __init__(
        self,
        cliente_id: str,
        fact_repo: FactRepository,
        canonical_repo: CanonicalRepository,
        entity_repo: EntityRepository,
        finding_repo: "FindingRepository | None" = None,
        communication_service: "FindingCommunicationService | None" = None,
        clarification_service: "ClarificationService | None" = None,
        action_proposal_service: "ActionProposalService | None" = None,
    ) -> None:
        if not cliente_id:
            raise ValueError("cliente_id is required for Pipeline")

        self.cliente_id = cliente_id

        self.fact_extraction_service = FactExtractionService(fact_repo)
        self.canonicalization_service = CanonicalizationService(canonical_repo)
        self.entity_resolution_service = EntityResolutionService(entity_repo)
        self.comparison_service = ComparisonService()
        self.findings_service = FindingsService()

        self.fact_repo = fact_repo
        self.canonical_repo = canonical_repo
        self.entity_repo = entity_repo
        self.finding_repo = finding_repo
        self.communication_service = communication_service
        self.clarification_service = clarification_service
        self.action_proposal_service = action_proposal_service

    def _process_one_text(self, evidence_id: str, text: str, job_id=None, plan_id=None):
        self.fact_extraction_service.extract_from_evidence(
            evidence_id=evidence_id, text=text, job_id=job_id, plan_id=plan_id
        )
        facts = self.fact_repo.list_facts(evidence_id=evidence_id)
        self.canonicalization_service.canonicalize_facts(facts=facts, job_id=job_id, plan_id=plan_id)
        canonical_rows = self.canonical_repo.list_canonical_rows(evidence_id=evidence_id)
        self.entity_resolution_service.resolve_entities(
            canonical_rows=canonical_rows, job_id=job_id, plan_id=plan_id
        )

    def process_texts(self, evidence_id_a, text_a, evidence_id_b, text_b, job_id=None, plan_id=None):
        errors = []

        if (
            self.clarification_service is not None
            and self.clarification_service.has_pending_blockers(job_id=job_id)
        ):
            blocking_reason = f"BLOCKED for cliente_id={self.cliente_id}"
            return PipelineResult(
                cliente_id=self.cliente_id,
                status="BLOCKED",
                job_id=job_id,
                plan_id=plan_id,
                facts=[], canonical=[], entities=[], comparison=[], findings=[], messages=[], action_proposals=[],
                counts=_BLOCKED_COUNTS,
                errors=[blocking_reason],
                blocking_reason=blocking_reason,
            )

        self._process_one_text(evidence_id_a, text_a, job_id, plan_id)
        self._process_one_text(evidence_id_b, text_b, job_id, plan_id)

        facts = self.fact_repo.list_facts(evidence_id=evidence_id_a) + self.fact_repo.list_facts(evidence_id=evidence_id_b)
        canonical = self.canonical_repo.list_canonical_rows(evidence_id=evidence_id_a) + self.canonical_repo.list_canonical_rows(evidence_id=evidence_id_b)
        entities = self.entity_repo.list_entities()
        validated_entities = [e for e in entities if e.validation_status == "validated"]

        comparison_results = self.comparison_service.compare_entities(validated_entities)
        findings = self.findings_service.generate_findings(comparison_results)

        if self.finding_repo and findings:
            self.finding_repo.save_batch(findings)

        messages = self.communication_service.build_messages(findings) if self.communication_service else []
        action_proposals = self.action_proposal_service.propose_batch_from_messages(messages) if self.action_proposal_service and messages else []

        counts = PipelineCounts(
            facts=len(facts), canonical=len(canonical), entities=len(entities), validated_entities=len(validated_entities),
            comparison=len(comparison_results), findings=len(findings), messages=len(messages), action_proposals=len(action_proposals)
        )

        return PipelineResult(
            cliente_id=self.cliente_id,
            status="OK" if not errors else "ERROR",
            job_id=job_id,
            plan_id=plan_id,
            facts=facts,
            canonical=canonical,
            entities=entities,
            comparison=comparison_results,
            findings=findings,
            messages=messages,
            action_proposals=action_proposals,
            counts=counts,
            errors=errors,
            blocking_reason=None,
        )
