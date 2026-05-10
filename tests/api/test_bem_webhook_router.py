from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.bem_webhook_router import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _valid_request() -> dict:
    return {
        "tenant_id": "tenant-1",
        "payload": {
            "evidence_id": "ev-001",
            "kind": "excel",
            "data": {"sheet": "ventas", "rows": 10},
            "source": {
                "source_name": "upload_owner",
                "source_type": "excel_file",
            },
            "confidence": {"score": 0.9, "provider": "bem"},
            "trace_id": "trace-123",
        },
    }


def test_bem_webhook_valid_request() -> None:
    client = _client()

    res = client.post("/webhooks/bem", json=_valid_request())

    assert res.status_code == 200
    assert res.json() == {
        "status": "accepted",
        "evidence_id": "ev-001",
        "tenant_id": "tenant-1",
    }


def test_bem_webhook_rejects_missing_tenant() -> None:
    client = _client()
    payload = _valid_request()
    del payload["tenant_id"]

    res = client.post("/webhooks/bem", json=payload)

    assert res.status_code == 400
    assert "tenant_id" in res.json()["detail"]


def test_bem_webhook_rejects_invalid_payload() -> None:
    client = _client()
    body = {"tenant_id": "tenant-1", "payload": "invalid"}

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 400
    assert "payload" in res.json()["detail"]


def test_bem_webhook_rejects_invalid_kind() -> None:
    client = _client()
    payload = _valid_request()
    payload["payload"]["kind"] = "invalid-kind"

    res = client.post("/webhooks/bem", json=payload)

    assert res.status_code == 400
    assert "kind inválido" in res.json()["detail"]


def test_bem_webhook_rejects_missing_evidence_id() -> None:
    client = _client()
    payload = _valid_request()
    del payload["payload"]["evidence_id"]

    res = client.post("/webhooks/bem", json=payload)

    assert res.status_code == 400
    assert "evidence_id" in res.json()["detail"]


def test_bem_webhook_response_shape() -> None:
    client = _client()

    res = client.post("/webhooks/bem", json=_valid_request())
    body = res.json()

    assert res.status_code == 200
    assert body["status"] == "accepted"
    assert body["evidence_id"] == "ev-001"
    assert body["tenant_id"] == "tenant-1"


def test_bem_webhook_fail_closed_on_empty_body() -> None:
    client = _client()

    res = client.post("/webhooks/bem", json={})

    assert res.status_code == 400
