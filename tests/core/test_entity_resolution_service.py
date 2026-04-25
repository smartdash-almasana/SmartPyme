import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.evidence_contract import CanonicalRowCandidate
from app.repositories.entity_repository import EntityRepository
from app.services.entity_resolution_service import EntityResolutionService


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_entity_resolution"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"entities-{uuid.uuid4().hex[:8]}.db"


def _canonical_row(
    canonical_row_id: str,
    *,
    entity_type: str,
    value: str
) -> CanonicalRowCandidate:
    return CanonicalRowCandidate(
        canonical_row_id=canonical_row_id,
        fact_candidate_id="fact-1",
        evidence_id="ev-1",
        job_id=None,
        plan_id=None,
        entity_type=entity_type,
        row={"fact_type": entity_type, "value": value},
    )


def test_resolve_entities_creates_new_entity():
    repo = EntityRepository(_db_path())
    service = EntityResolutionService(repo)

    rows = [_canonical_row("row-1", entity_type="person", value="John Doe")]
    result = service.resolve_entities(rows, job_id="job-1")

    assert result["status"] == "RESOLVED"
    assert result["entities_count"] == 1
    
    entity = repo.find_by_attribute("person", "value", "John Doe")
    assert entity is not None
    assert entity.attributes["value"] == "John Doe"

def test_resolve_entities_merges_with_existing_entity():
    repo = EntityRepository(_db_path())
    service = EntityResolutionService(repo)

    # First, create an entity
    service.resolve_entities([
        _canonical_row("row-1", entity_type="person", value="Jane Doe")
    ])
    
    # Then, resolve a new row that should merge with the existing entity
    result = service.resolve_entities([
        _canonical_row("row-2", entity_type="person", value="Jane Doe")
    ], job_id="job-2")

    assert result["status"] == "RESOLVED"
    assert result["entities_count"] == 1
    
    entity = repo.find_by_attribute("person", "value", "Jane Doe")
    assert entity is not None
    # The entity id should be the same as the first one
    assert len(entity.linked_canonical_rows) == 2
