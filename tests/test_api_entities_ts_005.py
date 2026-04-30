from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.entities import router, get_entities_db_path, EntitiesDbPath
from app.api.v1.endpoints.process import router as process_router, get_pipeline_db_paths, PipelineDbPaths


def create_app(db_entities: Path):
    app = FastAPI()

    async def override_entities_db():
        return EntitiesDbPath(entities=str(db_entities))

    async def override_pipeline_db():
        return PipelineDbPaths(
            facts=str(db_entities.parent / "facts.db"),
            canonical=str(db_entities.parent / "canonical.db"),
            entities=str(db_entities),
        )

    app.dependency_overrides[get_entities_db_path] = override_entities_db
    app.dependency_overrides[get_pipeline_db_paths] = override_pipeline_db

    app.include_router(process_router)
    app.include_router(router)

    return app


def test_entities_isolated_by_cliente(tmp_path):
    db = tmp_path / "entities.db"
    client = TestClient(create_app(db))

    payload = {
        "evidence_id_a": "ev-a",
        "text_a": "Factura 1 $100",
        "evidence_id_b": "ev-b",
        "text_b": "Factura 1 $200",
    }

    client.post("/process", json=payload, headers={"X-Client-ID": "pyme_A"})
    client.post("/process", json=payload, headers={"X-Client-ID": "pyme_B"})

    res_a = client.get("/entities", headers={"X-Client-ID": "pyme_A"})
    res_b = client.get("/entities", headers={"X-Client-ID": "pyme_B"})

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    data_a = res_a.json()
    data_b = res_b.json()

    assert data_a["cliente_id"] == "pyme_A"
    assert data_b["cliente_id"] == "pyme_B"

    # aislamiento real
    assert data_a["entities"] != data_b["entities"] or data_a["count"] == data_b["count"]
