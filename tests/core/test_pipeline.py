import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.pipeline import Pipeline
from app.contracts.entity_contract import Entity
from app.contracts.pipeline_contract import PipelineResult
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository

TEST_TENANT_ID = "test_cliente"


def _db_path(name: str) -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / f"tmp_pipeline_{name}"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{name}-{uuid.uuid4().hex[:8]}.db"


def _make_pipeline() -> tuple[Pipeline, EntityRepository]:
    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(TEST_TENANT_ID, _db_path("entities"))
    pipeline = Pipeline(
        cliente_id=TEST_TENANT_ID,
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
    )
    return pipeline, entity_repo


def _seed_validated_entities(entity_repo: EntityRepository) -> None:
    """Seed two validated entities with different prices for the same CUIT."""
    entity_repo.save(Entity(
        entity_id="cuit-a",
        entity_type="cuit",
        attributes={"value": "20-12345678-3", "price": 1500.25},
        validation_status="validated",
    ))
    entity_repo.save(Entity(
        entity_id="cuit-b",
        entity_type="cuit",
        attributes={"value": "20-12345678-3", "price": 1800.00},
        validation_status="validated",
    ))


TEXT_A = "Factura 20-12345678-3 emitida el 15/04/2026 por $1500.25."
TEXT_B = "Factura 20-12345678-3 emitida el 15/04/2026 por $1800.00."


def test_pipeline_process_texts_generates_findings():
    pipeline, entity_repo = _make_pipeline()
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-1",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert len(result.comparison) == 1
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.severity == "ALTO"
    assert finding.difference == 299.75


def test_pipeline_returns_counts():
    pipeline, entity_repo = _make_pipeline()
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-counts",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert result.counts.facts > 0
    assert result.counts.canonical > 0
    assert result.counts.entities > 0
    assert result.counts.validated_entities >= 2
    assert result.counts.comparison == len(result.comparison)
    assert result.counts.findings == len(result.findings)


def test_pipeline_returns_empty_findings_when_no_differences():
    pipeline, entity_repo = _make_pipeline()
    entity_repo.save(Entity(
        entity_id="cuit-x",
        entity_type="cuit",
        attributes={"value": "30-99999999-9", "price": 500.00},
        validation_status="validated",
    ))
    entity_repo.save(Entity(
        entity_id="cuit-y",
        entity_type="cuit",
        attributes={"value": "30-99999999-9", "price": 500.00},
        validation_status="validated",
    ))

    text = "Factura 30-99999999-9 emitida el 15/04/2026 por $500.00."
    result = pipeline.process_texts(
        evidence_id_a="ev-x", text_a=text,
        evidence_id_b="ev-y", text_b=text,
        job_id="job-nodiff",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert result.findings == []
    assert result.counts.findings == 0


def test_pipeline_persists_findings_when_finding_repo_configured():
    from app.repositories.finding_repository import FindingRepository

    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(TEST_TENANT_ID, _db_path("entities"))
    finding_repo = FindingRepository(_db_path("findings"))

    pipeline = Pipeline(
        cliente_id=TEST_TENANT_ID,
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
        finding_repo=finding_repo,
    )
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-persist",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert len(result.findings) == 1

    persisted = finding_repo.list_findings()
    assert len(persisted) == 1
    assert persisted[0].finding_id == result.findings[0].finding_id
    assert persisted[0].severity == result.findings[0].severity
    assert persisted[0].difference == result.findings[0].difference


def test_pipeline_generates_messages_when_communication_service_configured():
    from app.services.finding_communication_service import FindingCommunicationService
    from app.contracts.communication_contract import FindingMessage

    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(TEST_TENANT_ID, _db_path("entities"))

    pipeline = Pipeline(
        cliente_id=TEST_TENANT_ID,
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
        communication_service=FindingCommunicationService(),
    )
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-messages",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert len(result.findings) == 1
    assert len(result.messages) == 1
    assert result.counts.messages == 1

    msg = result.messages[0]
    assert isinstance(msg, FindingMessage)
    assert msg.finding_id == result.findings[0].finding_id
    assert msg.channel == "internal"
    assert msg.severity == result.findings[0].severity


def test_pipeline_messages_empty_without_communication_service():
    pipeline, entity_repo = _make_pipeline()
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-no-comm",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert result.messages == []
    assert result.counts.messages == 0


def test_pipeline_blocked_when_clarification_pending():
    from app.repositories.clarification_repository import ClarificationRepository
    from app.services.clarification_service import ClarificationService

    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(TEST_TENANT_ID, _db_path("entities"))
    clarif_repo = ClarificationRepository(_db_path("clarif"))
    clarif_service = ClarificationService(clarif_repo)

    clarif_service.create_blocking_clarification(
        question="¿El monto es correcto?",
        reason="Diferencia detectada",
        job_id="job-blocked",
    )

    pipeline = Pipeline(
        cliente_id=TEST_TENANT_ID,
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
        clarification_service=clarif_service,
    )
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-blocked",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert result.status == "BLOCKED"
    assert result.blocking_reason is not None
    assert result.comparison == []
    assert result.findings == []
    assert result.messages == []
    assert len(result.errors) == 1


def test_pipeline_not_blocked_when_clarification_answered():
    from app.repositories.clarification_repository import ClarificationRepository
    from app.services.clarification_service import ClarificationService

    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(TEST_TENANT_ID, _db_path("entities"))
    clarif_repo = ClarificationRepository(_db_path("clarif"))
    clarif_service = ClarificationService(clarif_repo)

    c = clarif_service.create_blocking_clarification(
        question="¿El monto es correcto?",
        reason="Diferencia detectada",
        job_id="job-answered",
    )
    clarif_service.answer_clarification(c.clarification_id, answer="Sí, confirmado.")

    pipeline = Pipeline(
        cliente_id=TEST_TENANT_ID,
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
        clarification_service=clarif_service,
    )
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-answered",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert result.status == "OK"
    assert result.blocking_reason is None
    assert len(result.findings) == 1


def test_pipeline_generates_action_proposals_when_service_configured():
    from app.services.finding_communication_service import FindingCommunicationService
    from app.services.action_proposal_service import ActionProposalService
    from app.contracts.action_contract import ActionProposal

    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(TEST_TENANT_ID, _db_path("entities"))

    pipeline = Pipeline(
        cliente_id=TEST_TENANT_ID,
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
        communication_service=FindingCommunicationService(),
        action_proposal_service=ActionProposalService(),
    )
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-proposals",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert len(result.messages) == 1
    assert len(result.action_proposals) == 1
    assert result.counts.action_proposals == 1

    proposal = result.action_proposals[0]
    assert isinstance(proposal, ActionProposal)
    assert proposal.status == "proposed"
    assert proposal.source_type == "message"
    assert proposal.source_id == result.messages[0].message_id


def test_pipeline_action_proposals_empty_without_service():
    pipeline, entity_repo = _make_pipeline()
    _seed_validated_entities(entity_repo)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=TEXT_A,
        evidence_id_b="ev-b", text_b=TEXT_B,
        job_id="job-no-proposals",
    )

    assert result.cliente_id == TEST_TENANT_ID
    assert result.action_proposals == []
    assert result.counts.action_proposals == 0
