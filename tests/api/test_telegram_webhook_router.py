from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.telegram_webhook_router import get_telegram_adapter, router


class _FakeAdapter:
    def __init__(self, response: dict):
        self.response = response
        self.calls: list[dict] = []

    def handle_update(self, update: dict) -> dict:
        self.calls.append(update)
        return dict(self.response)


def _app_with_adapter(fake_adapter: _FakeAdapter) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_telegram_adapter] = lambda: fake_adapter
    return app


def test_webhook_telegram_xlsx_update_calls_adapter_and_returns_ok() -> None:
    fake = _FakeAdapter({"status": "queued", "message": "ok"})
    client = TestClient(_app_with_adapter(fake))

    res = client.post(
        "/webhook/telegram",
        json={
            "message": {
                "from": {"id": 42},
                "document": {"file_id": "f1", "file_name": "ventas.xlsx"},
            }
        },
    )

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["result"]["status"] == "queued"
    assert fake.calls[0]["message"]["document"]["file_name"] == "ventas.xlsx"


def test_webhook_telegram_invalid_update_does_not_crash() -> None:
    fake = _FakeAdapter({"status": "security_error", "message": "Falta telegram_user_id en el update."})
    client = TestClient(_app_with_adapter(fake))

    res = client.post("/webhook/telegram", json={})

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["result"]["status"] == "security_error"


def test_webhook_telegram_response_does_not_expose_tokens() -> None:
    fake = _FakeAdapter(
        {
            "status": "queued",
            "telegram_bot_token": "TOKEN-SECRET",
            "api_key": "API-SECRET",
            "message": "safe",
        }
    )
    client = TestClient(_app_with_adapter(fake))

    res = client.post("/webhook/telegram", json={"message": {"from": {"id": 42}}})

    assert res.status_code == 200
    body = res.json()
    assert "telegram_bot_token" not in body["result"]
    assert "api_key" not in body["result"]
    assert body["result"]["message"] == "safe"
