import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.contracts.entity_contract import Entity
from app.repositories.entity_repository import EntityRepository

TEST_CLIENTE_ID = "test_cliente"


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[2] / "fixtures" / "tmp_entity_repository"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"entities-{uuid.uuid4().hex[:8]}.db"


def _repo() -> EntityRepository:
    return EntityRepository(TEST_CLIENTE_ID, _db_path())


def _entity(
    entity_id: str,
    *,
    entity_type: str = "person",
    attributes: dict | None = None,
) -> Entity:
    return Entity(
        entity_id=entity_id,
        entity_type=entity_type,
        attributes=attributes or {"name": "John Doe"},
    )


def test_entity_repository_init_save_and_find():
    repo = _repo()
    entity = _entity("entity-1", attributes={"name": "Jane Doe"})

    repo.save(entity)
    found_entity = repo.find_by_attribute("person", "name", "Jane Doe")

    assert found_entity is not None
    assert found_entity.entity_id == "entity-1"


def test_entity_repository_find_by_attribute_exact_match():
    repo = _repo()
    entity = _entity("entity-2", attributes={"value": "123.45"})
    repo.save(entity)

    found_entity = repo.find_by_attribute("person", "value", "123.45")
    assert found_entity is not None
    assert found_entity.entity_id == "entity-2"

    not_found_entity = repo.find_by_attribute("person", "value", "123.46")
    assert not_found_entity is None


def test_entity_repository_save_is_idempotent_by_entity_id():
    repo = _repo()
    repo.save(_entity("entity-1"))
    repo.save(_entity("entity-1"))
    found_entity = repo.find_by_attribute("person", "name", "John Doe")
    assert found_entity is not None


def test_entity_repository_save_batch():
    repo = _repo()
    repo.save_batch([
        _entity("entity-1", attributes={"name": "Person 1"}),
        _entity("entity-2", entity_type="company", attributes={"name": "Company 1"}),
    ])
    assert repo.find_by_attribute("person", "name", "Person 1") is not None
    assert repo.find_by_attribute("company", "name", "Company 1") is not None


def test_entity_repository_list_entities():
    repo = _repo()
    repo.save_batch([
        _entity("entity-1", entity_type="person"),
        _entity("entity-2", entity_type="company"),
        _entity("entity-3", entity_type="person"),
    ])

    all_entities = repo.list_entities()
    assert len(all_entities) == 3

    person_entities = repo.list_entities(entity_type="person")
    assert len(person_entities) == 2

    company_entities = repo.list_entities(entity_type="company")
    assert len(company_entities) == 1
