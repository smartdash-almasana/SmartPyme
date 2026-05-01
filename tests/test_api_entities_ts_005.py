from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.entities import EntitiesDbPath, get_entities_db_path, router
from app.contracts.entity_contract import Entity
from app.repositories.entity_repository import EntityRepository


def create_app(db_entities: Path):
    app = FastAPI()

    async def override_entities_db():
        return EntitiesDbPath(entities=str(db_entities))

    app.dependency_overrides[get_entities_db_path] = override_entities_db
    app.include_router(router)

    return app


def test_entities_isolated_by_cliente_shared_db(tmp_path):
    db = tmp_path / "entities.db"

    repo_a = EntityRepository("pyme_A", db)
    repo_b = EntityRepository("pyme_B", db)

    repo_a.save(Entity(
        entity_id="same-business-id",
        entity_type="customer",
        attributes={"name": "Cliente A", "owner": "pyme_A"},
        validation_status="validated",
    ))
    repo_b.save(Entity(
        entity_id="same-business-id",
        entity_type="customer",
        attributes={"name": "Cliente B", "owner": "pyme_B"},
        validation_status="validated",
    ))

    client = TestClient(create_app(db))

    res_a = client.get("/entities", headers={"X-Client-ID": "pyme_A"})
    res_b = client.get("/entities", headers={"X-Client-ID": "pyme_B"})

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    data_a = res_a.json()
    data_b = res_b.json()

    assert data_a["cliente_id"] == "pyme_A"
    assert data_b["cliente_id"] == "pyme_B"

    assert data_a["count"] == 1
    assert data_b["count"] == 1

    entity_a = data_a["entities"][0]
    entity_b = data_b["entities"][0]

    assert entity_a["entity_id"] == "same-business-id"
    assert entity_b["entity_id"] == "same-business-id"

    assert entity_a["attributes"]["owner"] == "pyme_A"
    assert entity_b["attributes"]["owner"] == "pyme_B"

    assert entity_a["attributes"]["owner"] != entity_b["attributes"]["owner"]
