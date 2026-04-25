import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.pipeline import Pipeline
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository


def _db_path(name: str) -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / f"tmp_orchestrator_{name}"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{name}-{uuid.uuid4().hex[:8]}.db"


def test_pipeline_process_text():
    fact_repo = FactRepository(_db_path("facts"))
    canonical_repo = CanonicalRepository(_db_path("canonical"))
    entity_repo = EntityRepository(_db_path("entities"))

    orchestrator = Pipeline(
        fact_repo=fact_repo,
        canonical_repo=canonical_repo,
        entity_repo=entity_repo,
    )

    text = "Factura 20-12345678-3 emitida el 15/04/2026 por $1500.25."
    result = orchestrator.process_text(evidence_id="ev-1", text=text, job_id="job-1")

    assert result["fact_extraction"]["facts_count"] == 3
    assert result["canonicalization"]["canonical_rows_count"] == 3
    assert result["entity_resolution"]["entities_count"] == 3
