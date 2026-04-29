from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.auth_check import router


def create_app():
    app = FastAPI()
    app.include_router(router)
    return app


def test_whoami_block_without_header():
    app = create_app()
    client = TestClient(app)

    response = client.get("/auth/whoami")

    assert response.status_code == 403
    assert "Falta Identidad" in response.json()["detail"]


def test_whoami_success_with_header():
    app = create_app()
    client = TestClient(app)

    response = client.get(
        "/auth/whoami",
        headers={"X-Client-ID": "pyme_test"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "sovereign"
    assert data["cliente_id"] == "pyme_test"
