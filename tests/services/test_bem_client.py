from __future__ import annotations

import json

import pytest

from app.services.bem_client import BemClient, httpx


pytestmark = pytest.mark.skipif(httpx is None, reason="httpx no disponible en entorno")


def test_submit_payload_ok_with_httpx_mock_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/workflows/wf-001/submit"
        assert request.headers["x-api-key"] == "secret-key"
        assert request.headers["content-type"] == "application/json"
        assert json.loads(request.content.decode("utf-8")) == {"foo": "bar"}
        return httpx.Response(status_code=200, json={"status": "ok", "id": "r-1"})

    client = BemClient(
        api_key="secret-key",
        base_url="https://api.bem.ai",
        transport=httpx.MockTransport(handler),
    )

    result = client.submit_payload("wf-001", {"foo": "bar"})

    assert result == {"status": "ok", "id": "r-1"}


def test_api_key_required() -> None:
    with pytest.raises(ValueError, match="api_key"):
        BemClient(api_key="")


def test_workflow_id_required() -> None:
    client = BemClient(api_key="k")
    with pytest.raises(ValueError, match="workflow_id"):
        client.submit_payload("", {"x": 1})


def test_payload_required() -> None:
    client = BemClient(api_key="k")
    with pytest.raises(ValueError, match="payload"):
        client.submit_payload("wf-1", {})


def test_fail_closed_on_http_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=400, json={"error": "bad_request"})

    client = BemClient(api_key="k", transport=httpx.MockTransport(handler))
    with pytest.raises(RuntimeError, match="HTTP 400"):
        client.submit_payload("wf-1", {"x": 1})


def test_fail_closed_on_non_object_json_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json=["unexpected"])

    client = BemClient(api_key="k", transport=httpx.MockTransport(handler))
    with pytest.raises(TypeError, match="JSON object"):
        client.submit_payload("wf-1", {"x": 1})


def test_api_key_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json={"ok": True})

    monkeypatch.setenv("BEM_API_KEY", "env-key")
    client = BemClient(transport=httpx.MockTransport(handler))
    result = client.submit_payload("wf-1", {"x": 1})

    assert result == {"ok": True}
