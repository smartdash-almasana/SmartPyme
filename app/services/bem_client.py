from __future__ import annotations

import json
import os
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

    def submit_payload(self, workflow_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise ValueError("workflow_id es obligatorio")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload es obligatorio y no puede estar vacío")

        url = f"{self._base_url}/v3/workflows/{workflow_id.strip()}/call?wait=true"
        headers = {
            "x-api-key": self._api_key,
            "content-type": "application/json",
        }
        request_body = {"input": payload}

        if httpx is not None:
            return self._submit_with_httpx(url, headers, request_body)
        if requests is not None:
            return self._submit_with_requests(url, headers, request_body)
        return self._submit_with_urllib(url, headers, request_body)

    def _submit_with_httpx(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        with httpx.Client(transport=self._transport, timeout=10.0) as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                raise RuntimeError(f"BEM error HTTP {response.status_code}")
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
            raise RuntimeError(f"BEM error HTTP {response.status_code}")
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
                if status_code >= 400:
                    raise RuntimeError(f"BEM error HTTP {status_code}")
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise RuntimeError(f"BEM error HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("BEM network error") from exc

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise TypeError("BEM response debe ser JSON object")
        return data
