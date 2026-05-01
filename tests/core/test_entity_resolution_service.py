import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.evidence_contract import CanonicalRowCandidate
from app.repositories.entity_repository import EntityRepository
from app.services.entity_resolution_service import EntityResolutionService

TEST_TENANT_ID = "test_cliente"


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_entity_resolution"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"entities-{uuid.uuid4().hex[:8]}.db"


def _entity_repo() -> EntityRepository:
    return EntityRepository(TEST_TENANT_ID, _db_path())


def _canonical_row(
    canonical_row_id: str,
    *,
    cliente_id: str = TEST_TENANT_ID,
    entity_type: str,
    value: str
) -> CanonicalRowCandidate:
    return CanonicalRowCandidate(
        cliente_id=cliente_id,
        canonical_row_id=canonical_row_id,
        fact_candidate_id="fact-1",
        evidence_id="ev-1",
        job_id=None,
        plan_id=None,
        entity_type=entity_type,
        row={"fact_type": entity_type, "value": value},
    )


def test_resolve_entities_creates_new_entity():
    repo = _entity_repo()
    service = EntityResolutionService(repo)

    rows = [_canonical_row("row-1", entity_type="person", value="John Doe")]
    result = service.resolve_entities(rows, job_id="job-1")

    assert result["status"] == "RESOLVED"
    assert result["entities_count"] == 1
    
    entity = repo.find_by_attribute("person", "value", "John Doe")
    assert entity is not None
    assert entity.attributes["value"] == "John Doe"


def test_resolve_entities_merges_with_existing_entity():
    repo = _entity_repo()
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


def test_resolve_entities_preserves_validated_status():
    """Una entidad con validation_status='validated' no debe ser degradada a pending_validation."""
    from app.contracts.entity_contract import Entity

    repo = _entity_repo()
    service = EntityResolutionService(repo)

    # Pre-cargar entidad ya validada por un humano.
    validated_entity = Entity(
        entity_id="ent-validated-1",
        entity_type="person",
        attributes={"value": "Alice", "score": 99},
        linked_canonical_rows=["row-0"],
        validation_status="validated",
    )
    repo.save(validated_entity)

    # Resolver una nueva canonical row que matchea la misma entidad.
    result = service.resolve_entities([
        _canonical_row("row-1", entity_type="person", value="Alice")
    ], job_id="job-preserve")

    assert result["status"] == "RESOLVED"
    assert result["entities_count"] == 1

    entity = repo.find_by_attribute("person", "value", "Alice")
    assert entity is not None
    # El status validado debe conservarse.
    assert entity.validation_status == "validated"
    # El nuevo canonical_row_id debe estar vinculado.
    assert "row-1" in entity.linked_canonical_rows
    # El canonical_row_id original no debe perderse.
    assert "row-0" in entity.linked_canonical_rows
