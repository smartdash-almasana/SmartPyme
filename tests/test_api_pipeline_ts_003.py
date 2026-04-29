from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.process import router


def create_app():
    app = FastAPI()
    app.include_router(router)
    return app


def test_process_block_without_header():
    client = TestClient(create_app())

    response = client.post("/process", json={})
    assert response.status_code == 403


def test_process_success_with_header():
    client = TestClient(create_app())

    payload = {
        "evidence_id_a": "ev-a",
        "text_a": "Factura 1 $100",
        "evidence_id_b": "ev-b",
        "text_b": "Factura 1 $200",
    }

    response = client.post(
        "/process",
        json=payload,
        headers={"X-Client-ID": "pyme_test"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["cliente_id"] == "pyme_test"
