from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.bem_client import BemClient, httpx


pytestmark = pytest.mark.skipif(httpx is None, reason="httpx no disponible en entorno")


def test_submit_payload_ok_with_httpx_mock_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v3/workflows/wf-001/call"
        assert request.url.query == b"wait=true"
        assert request.headers["x-api-key"] == "secret-key"
        assert request.headers["content-type"] == "application/json"
        assert json.loads(request.content.decode("utf-8")) == {"input": {"foo": "bar"}}
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


def test_submit_file_valido(tmp_path: Path) -> None:
    file_path = tmp_path / "ventas.xlsx"
    file_path.write_bytes(b"fake-xlsx-content")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v3/workflows/wf-file/call"
        assert request.url.query == b"wait=true"
        assert request.headers["x-api-key"] == "secret-key"
        assert "multipart/form-data" in request.headers["content-type"]
        content = request.content
        assert b'name="file"' in content
        assert b'filename="ventas.xlsx"' in content
        assert b"fake-xlsx-content" in content
        return httpx.Response(status_code=200, json={"status": "ok-file"})

    client = BemClient(
        api_key="secret-key",
        transport=httpx.MockTransport(handler),
    )

    result = client.submit_file("wf-file", file_path)

    assert result == {"status": "ok-file"}


def test_submit_file_archivo_inexistente() -> None:
    client = BemClient(api_key="k")
    with pytest.raises(ValueError, match="file_path"):
        client.submit_file("wf-file", "no-existe.xlsx")


def test_submit_file_workflow_vacio(tmp_path: Path) -> None:
    file_path = tmp_path / "ventas.xlsx"
    file_path.write_bytes(b"abc")
    client = BemClient(api_key="k")
    with pytest.raises(ValueError, match="workflow_id"):
        client.submit_file("", file_path)


def test_submit_file_response_json_parseado(tmp_path: Path) -> None:
    file_path = tmp_path / "ventas_demo_bem.xlsx"
    file_path.write_bytes(b"content")

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json={"runId": "bem-777", "status": "ok"})

    client = BemClient(api_key="secret-key", transport=httpx.MockTransport(handler))
    result = client.submit_file("smartpyme-venta-bajo-costo", file_path)

    assert result == {"runId": "bem-777", "status": "ok"}


def test_submit_file_call_reference_id_enviado(tmp_path: Path) -> None:
    file_path = tmp_path / "ventas_demo_bem.xlsx"
    file_path.write_bytes(b"content")

    def handler(request: httpx.Request) -> httpx.Response:
        content = request.content
        assert b'name="callReferenceID"' in content
        assert b"ref-123" in content
        return httpx.Response(status_code=200, json={"ok": True})

    client = BemClient(api_key="secret-key", transport=httpx.MockTransport(handler))
    result = client.submit_file("wf-file", file_path, call_reference_id="ref-123")

    assert result == {"ok": True}


@pytest.mark.parametrize(
    ("filename", "expected_mime"),
    [
        ("archivo.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("archivo.xls", "application/vnd.ms-excel"),
        ("archivo.csv", "text/csv"),
        ("archivo.pdf", "application/pdf"),
        ("archivo.bin", "application/octet-stream"),
    ],
)
def test_submit_file_mime_por_extension(tmp_path: Path, filename: str, expected_mime: str) -> None:
    file_path = tmp_path / filename
    file_path.write_bytes(b"content")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v3/workflows/wf-file/call"
        assert request.url.query == b"wait=true"
        body = request.content
        assert f"Content-Type: {expected_mime}".encode("utf-8") in body
        return httpx.Response(status_code=200, json={"ok": True})

    client = BemClient(api_key="secret-key", transport=httpx.MockTransport(handler))
    result = client.submit_file("wf-file", file_path)
    assert result == {"ok": True}
