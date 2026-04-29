from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.process import router, get_pipeline_db_paths, PipelineDbPaths


def create_app(db_paths: PipelineDbPaths):
    app = FastAPI()

    async def override_db_paths():
        return db_paths

    app.dependency_overrides[get_pipeline_db_paths] = override_db_paths
    app.include_router(router)
    return app


def test_no_leak_between_clients_shared_db(tmp_path):
    shared = tmp_path / "shared_entities.db"

    db_paths = PipelineDbPaths(
        facts=str(tmp_path / "facts.db"),
        canonical=str(tmp_path / "canonical.db"),
        entities=str(shared),
    )

    client = TestClient(create_app(db_paths))

    payload = {
        "evidence_id_a": "ev-a",
        "text_a": "Factura 1 $100",
        "evidence_id_b": "ev-b",
        "text_b": "Factura 1 $200",
    }

    res_a = client.post(
        "/process",
        json=payload,
        headers={"X-Client-ID": "pyme_A"},
    )

    res_b = client.post(
        "/process",
        json=payload,
        headers={"X-Client-ID": "pyme_B"},
    )

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    data_a = res_a.json()
    data_b = res_b.json()

    assert data_a["cliente_id"] == "pyme_A"
    assert data_b["cliente_id"] == "pyme_B"
    assert data_a["cliente_id"] != data_b["cliente_id"]
