import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contracts.entity_contract import Entity
from app.repositories.entity_repository import EntityRepository


def test_sovereignty_isolation_between_clients(tmp_path):
    db_file = tmp_path / "entities.db"

    repo_a = EntityRepository("pyme_1", db_file)
    repo_b = EntityRepository("pyme_2", db_file)

    entity = Entity(entity_id="entity-1", entity_type="person", attributes={"name": "Juan"})

    repo_a.save(entity)

    found_a = repo_a.find_by_attribute("person", "name", "Juan")
    found_b = repo_b.find_by_attribute("person", "name", "Juan")

    assert found_a is not None
    assert found_b is None
