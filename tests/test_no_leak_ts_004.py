from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.process import router


def create_app():
    app = FastAPI()
    app.include_router(router)
    return app


def test_no_leak_between_clients():
    client = TestClient(create_app())

    payload = {
        "evidence_id_a": "ev-a",
        "text_a": "Factura 1 $100",
        "evidence_id_b": "ev-b",
        "text_b": "Factura 1 $200",
    }

    response_a = client.post(
        "/process",
        json=payload,
        headers={"X-Client-ID": "pyme_A"},
    )
    response_b = client.post(
        "/process",
        json=payload,
        headers={"X-Client-ID": "pyme_B"},
    )

    assert response_a.status_code == 200
    assert response_b.status_code == 200

    data_a = response_a.json()
    data_b = response_b.json()

    assert data_a["cliente_id"] == "pyme_A"
    assert data_b["cliente_id"] == "pyme_B"
    assert data_a["cliente_id"] != data_b["cliente_id"]
