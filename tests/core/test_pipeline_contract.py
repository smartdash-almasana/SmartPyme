"""
Tests de contrato para PipelineResult.
Verifican que la salida del pipeline cumple el contrato definido en
app/contracts/pipeline_contract.py, independientemente de los datos concretos.
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.pipeline import Pipeline
from app.contracts.entity_contract import Entity
from app.contracts.pipeline_contract import PipelineCounts, PipelineResult
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository


def _db_path(name: str) -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / f"tmp_pipeline_contract_{name}"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{name}-{uuid.uuid4().hex[:8]}.db"


def _make_pipeline() -> tuple[Pipeline, EntityRepository]:
    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(_db_path("entities"))
    pipeline = Pipeline(
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
    )
    return pipeline, entity_repo


def test_pipeline_result_is_pipeline_result_instance():
    pipeline, entity_repo = _make_pipeline()
    entity_repo.save(Entity(
        entity_id="e1", entity_type="cuit",
        attributes={"value": "20-11111111-1", "price": 100.0},
        validation_status="validated",
    ))
    entity_repo.save(Entity(
        entity_id="e2", entity_type="cuit",
        attributes={"value": "20-11111111-1", "price": 200.0},
        validation_status="validated",
    ))

    result = pipeline.process_texts(
        evidence_id_a="ev-1", text_a="Factura 20-11111111-1 emitida el 01/01/2026 por $100.00.",
        evidence_id_b="ev-2", text_b="Factura 20-11111111-1 emitida el 01/01/2026 por $200.00.",
        job_id="job-contract",
    )

    assert isinstance(result, PipelineResult)


def test_pipeline_result_has_required_fields():
    pipeline, entity_repo = _make_pipeline()
    entity_repo.save(Entity(
        entity_id="e1", entity_type="cuit",
        attributes={"value": "20-22222222-2", "price": 100.0},
        validation_status="validated",
    ))
    entity_repo.save(Entity(
        entity_id="e2", entity_type="cuit",
        attributes={"value": "20-22222222-2", "price": 150.0},
        validation_status="validated",
    ))

    result = pipeline.process_texts(
        evidence_id_a="ev-1", text_a="Factura 20-22222222-2 emitida el 01/01/2026 por $100.00.",
        evidence_id_b="ev-2", text_b="Factura 20-22222222-2 emitida el 01/01/2026 por $150.00.",
        job_id="job-fields",
        plan_id="plan-1",
    )

    # Campos obligatorios del contrato
    assert result.status in ("OK", "ERROR")
    assert result.job_id == "job-fields"
    assert result.plan_id == "plan-1"
    assert isinstance(result.facts, list)
    assert isinstance(result.canonical, list)
    assert isinstance(result.entities, list)
    assert isinstance(result.comparison, list)
    assert isinstance(result.findings, list)
    assert isinstance(result.messages, list)
    assert isinstance(result.errors, list)
    assert isinstance(result.counts, PipelineCounts)


def test_pipeline_result_counts_are_consistent():
    pipeline, entity_repo = _make_pipeline()
    entity_repo.save(Entity(
        entity_id="e1", entity_type="cuit",
        attributes={"value": "20-33333333-3", "price": 300.0},
        validation_status="validated",
    ))
    entity_repo.save(Entity(
        entity_id="e2", entity_type="cuit",
        attributes={"value": "20-33333333-3", "price": 400.0},
        validation_status="validated",
    ))

    result = pipeline.process_texts(
        evidence_id_a="ev-1", text_a="Factura 20-33333333-3 emitida el 01/01/2026 por $300.00.",
        evidence_id_b="ev-2", text_b="Factura 20-33333333-3 emitida el 01/01/2026 por $400.00.",
        job_id="job-counts",
    )

    # counts deben ser coherentes con las listas reales
    assert result.counts.facts == len(result.facts)
    assert result.counts.canonical == len(result.canonical)
    assert result.counts.entities == len(result.entities)
    assert result.counts.comparison == len(result.comparison)
    assert result.counts.findings == len(result.findings)
    assert result.counts.messages == len(result.messages)
    assert result.counts.validated_entities <= result.counts.entities


def test_pipeline_result_status_ok_when_no_errors():
    pipeline, _ = _make_pipeline()

    result = pipeline.process_texts(
        evidence_id_a="ev-1", text_a="Texto sin datos relevantes.",
        evidence_id_b="ev-2", text_b="Otro texto sin datos relevantes.",
        job_id="job-ok",
    )

    assert result.status == "OK"
    assert result.errors == []


def test_pipeline_result_messages_empty_without_communication_service():
    pipeline, entity_repo = _make_pipeline()
    entity_repo.save(Entity(
        entity_id="e1", entity_type="cuit",
        attributes={"value": "20-44444444-4", "price": 100.0},
        validation_status="validated",
    ))
    entity_repo.save(Entity(
        entity_id="e2", entity_type="cuit",
        attributes={"value": "20-44444444-4", "price": 200.0},
        validation_status="validated",
    ))

    result = pipeline.process_texts(
        evidence_id_a="ev-1", text_a="Factura 20-44444444-4 emitida el 01/01/2026 por $100.00.",
        evidence_id_b="ev-2", text_b="Factura 20-44444444-4 emitida el 01/01/2026 por $200.00.",
        job_id="job-no-comm",
    )

    # No communication_service configured → messages must be empty.
    assert result.messages == []
    assert result.counts.messages == 0
