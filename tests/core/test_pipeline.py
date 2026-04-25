import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.pipeline import Pipeline
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository


def _db_path(name: str) -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / f"tmp_pipeline_{name}"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{name}-{uuid.uuid4().hex[:8]}.db"


def test_pipeline_process_texts_generates_findings():
    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(_db_path("entities"))

    pipeline = Pipeline(
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
    )

    text_a = "Factura 20-12345678-3 emitida el 15/04/2026 por $1500.25."
    text_b = "Factura 20-12345678-3 emitida el 15/04/2026 por $1800.00."

    from app.contracts.entity_contract import Entity
    entity_a = Entity(entity_id="cuit-a", entity_type="cuit", attributes={"value": "20-12345678-3", "price": 1500.25}, validation_status="validated")
    entity_b = Entity(entity_id="cuit-b", entity_type="cuit", attributes={"value": "20-12345678-3", "price": 1800.00}, validation_status="validated")
    entity_repo.save(entity_a)
    entity_repo.save(entity_b)

    result = pipeline.process_texts(
        evidence_id_a="ev-a", text_a=text_a, evidence_id_b="ev-b", text_b=text_b, job_id="job-1"
    )

    assert len(result["comparison"]) == 1
    assert len(result["findings"]) == 1
    finding = result["findings"][0]
    assert finding.severity == "ALTO"
    assert finding.difference == 299.75
