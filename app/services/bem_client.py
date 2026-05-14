from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

try:
    import httpx  # type: ignore
except Exception:  # pragma: no cover
    httpx = None  # type: ignore

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


class BemClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.bem.ai",
        *,
        transport: Any | None = None,
    ) -> None:
        resolved_api_key = api_key or os.getenv("BEM_API_KEY")
        if not isinstance(resolved_api_key, str) or not resolved_api_key.strip():
            raise ValueError("api_key es obligatoria")
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url es obligatoria")

        self._api_key = resolved_api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._transport = transport

    def submit_payload(
        self,
        workflow_id: str,
        payload: dict[str, Any],
        call_reference_id: str | None = None,
    ) -> dict[str, Any]:
        """Submit a BEM workflow JSON input body.

        BEM v3 workflow calls expect the business/document input under the
        top-level `input` key. For compatibility, callers may pass either:

        - the raw input object, for example `{ "singleFile": {...} }`; or
        - a full BEM call body, for example `{ "input": {"singleFile": {...}} }`.
        """
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise ValueError("workflow_id es obligatorio")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload es obligatorio y no puede estar vacío")
        if call_reference_id is not None and (
            not isinstance(call_reference_id, str) or not call_reference_id.strip()
        ):
            raise ValueError("call_reference_id inválido")

        url = f"{self._base_url}/v3/workflows/{workflow_id.strip()}/call?wait=true"
        headers = {
            "x-api-key": self._api_key,
            "content-type": "application/json",
        }
        request_body = _build_workflow_json_body(payload, call_reference_id)

        if httpx is not None:
            return self._submit_with_httpx(url, headers, request_body)
        if requests is not None:
            return self._submit_with_requests(url, headers, request_body)
        return self._submit_with_urllib(url, headers, request_body)

    def submit_file(
        self,
        workflow_id: str,
        file_path: str | Path,
        call_reference_id: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise ValueError("workflow_id es obligatorio")
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise ValueError("file_path no existe")
        if call_reference_id is not None and (
            not isinstance(call_reference_id, str) or not isinstance(call_reference_id, str) or not call_reference_id.strip()
        ):
            raise ValueError("call_reference_id inválido")

        url = f"{self._base_url}/v3/workflows/{workflow_id.strip()}/call?wait=true"
        headers = {
            "x-api-key": self._api_key,
        }
        file_bytes = path.read_bytes()
        filename = path.name
        content_type = _resolve_content_type(filename)

        if httpx is not None:
            return self._submit_file_with_httpx(
                url,
                headers,
                filename,
                file_bytes,
                content_type,
                call_reference_id,
            )
        if requests is not None:
            return self._submit_file_with_requests(
                url,
                headers,
                filename,
                file_bytes,
                content_type,
                call_reference_id,
            )
        return self._submit_file_with_urllib(
            url,
            headers,
            filename,
            file_bytes,
            content_type,
            call_reference_id,
        )

    def _submit_with_httpx(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        with httpx.Client(transport=self._transport, timeout=10.0) as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                raise RuntimeError(_format_bem_http_error(response.status_code, response.text))
            data = response.json()
            if not isinstance(data, dict):
                raise TypeError("BEM response debe ser JSON object")
            return data

    def _submit_with_requests(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        response = requests.post(url, headers=headers, json=payload, timeout=10.0)
        if response.status_code >= 400:
            raise RuntimeError(_format_bem_http_error(response.status_code, response.text))
        data = response.json()
        if not isinstance(data, dict):
            raise TypeError("BEM response debe ser JSON object")
        return data

    def _submit_with_urllib(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(url=url, method="POST", headers=headers, data=body)
        try:
            with urllib_request.urlopen(req, timeout=10.0) as response:
                status_code = getattr(response, "status", 200)
                raw = response.read().decode("utf-8")
                if status_code >= 400:
                    raise RuntimeError(_format_bem_http_error(status_code, raw))
        except HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8")
            except Exception:  # pragma: no cover
                error_body = ""
            raise RuntimeError(_format_bem_http_error(exc.code, error_body)) from exc
        except URLError as exc:
            raise RuntimeError("BEM network error") from exc

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise TypeError("BEM response debe ser JSON object")
        return data

    def _submit_file_with_httpx(
        self,
        url: str,
        headers: dict[str, str],
        filename: str,
        file_bytes: bytes,
        content_type: str,
        call_reference_id: str | None,
    ) -> dict[str, Any]:
        files = {
            "file": (filename, file_bytes, content_type),
        }
        data: dict[str, str] | None = None
        if call_reference_id is not None:
            data = {"callReferenceID": call_reference_id}
        with httpx.Client(transport=self._transport, timeout=10.0) as client:
            response = client.post(url, headers=headers, files=files, data=data)
            if response.status_code >= 400:
                raise RuntimeError(_format_bem_http_error(response.status_code, response.text))
            data = response.json()
            if not isinstance(data, dict):
                raise TypeError("BEM response debe ser JSON object")
            return data

    def _submit_file_with_requests(
        self,
        url: str,
        headers: dict[str, str],
        filename: str,
        file_bytes: bytes,
        content_type: str,
        call_reference_id: str | None,
    ) -> dict[str, Any]:
        files = {
            "file": (filename, file_bytes, content_type),
        }
        data: dict[str, str] | None = None
        if call_reference_id is not None:
            data = {"callReferenceID": call_reference_id}
        response = requests.post(url, headers=headers, files=files, data=data, timeout=10.0)
        if response.status_code >= 400:
            raise RuntimeError(_format_bem_http_error(response.status_code, response.text))
        data = response.json()
        if not isinstance(data, dict):
            raise TypeError("BEM response debe ser JSON object")
        return data

    def _submit_file_with_urllib(
        self,
        url: str,
        headers: dict[str, str],
        filename: str,
        file_bytes: bytes,
        content_type: str,
        call_reference_id: str | None,
    ) -> dict[str, Any]:
        boundary = "----SmartPymeBemBoundary7MA4YWxkTrZu0gW"
        multipart_headers = {
            **headers,
            "content-type": f"multipart/form-data; boundary={boundary}",
        }
        body = _build_multipart_body(
            boundary=boundary,
            field_name="file",
            filename=filename,
            file_bytes=file_bytes,
            content_type=content_type,
            call_reference_id=call_reference_id,
        )
        req = urllib_request.Request(url=url, method="POST", headers=multipart_headers, data=body)
        try:
            with urllib_request.urlopen(req, timeout=10.0) as response:
                status_code = getattr(response, "status", 200)
                raw = response.read().decode("utf-8")
                if status_code >= 400:
                    raise RuntimeError(_format_bem_http_error(status_code, raw))
        except HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8")
            except Exception:  # pragma: no cover
                error_body = ""
            raise RuntimeError(_format_bem_http_error(exc.code, error_body)) from exc
        except URLError as exc:
            raise RuntimeError("BEM network error") from exc

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise TypeError("BEM response debe ser JSON object")
        return data


def _build_workflow_json_body(
    payload: dict[str, Any], call_reference_id: str | None = None
) -> dict[str, Any]:
    if "input" in payload:
        input_payload = payload.get("input")
        if not isinstance(input_payload, dict) or not input_payload:
            raise ValueError("payload.input debe ser un objeto no vacío")
        request_body = dict(payload)
    else:
        request_body = {"input": payload}

    if call_reference_id is not None:
        request_body["callReferenceID"] = call_reference_id.strip()

    return request_body


def _format_bem_http_error(status_code: int, body: str | None = None) -> str:
    detail = ""
    if isinstance(body, str) and body.strip():
        sanitized = body.replace("\n", " ").replace("\r", " ").strip()
        detail = f": {sanitized[:500]}"
    return f"BEM error HTTP {status_code}{detail}"


def _build_multipart_body(
    *,
    boundary: str,
    field_name: str,
    filename: str,
    file_bytes: bytes,
    content_type: str,
    call_reference_id: str | None,
) -> bytes:
    line_break = b"\r\n"
    parts: list[bytes] = []
    if call_reference_id is not None:
        parts.extend(
            [
                f"--{boundary}".encode("utf-8"),
                b'Content-Disposition: form-data; name="callReferenceID"',
                b"",
                call_reference_id.encode("utf-8"),
            ]
        )
    parts.extend(
        [
            f"--{boundary}".encode("utf-8"),
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode(
                "utf-8"
            ),
            f"Content-Type: {content_type}".encode("utf-8"),
            b"",
            file_bytes,
            f"--{boundary}--".encode("utf-8"),
            b"",
        ]
    )
    return line_break.join(parts)


def _resolve_content_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if suffix == ".xls":
        return "application/vnd.ms-excel"
    if suffix == ".csv":
        return "text/csv"
    if suffix == ".pdf":
        return "application/pdf"
    return "application/octet-stream"
