from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

DEFAULT_FREE_MODELS = (
    "gemma-4",
    "qwen/qwen3-32b:free",
    "minimax/minimax-m1:free",
    "meta-llama/llama-3.3-70b-instruct:free",
)

_DEFAULT_PROMPT = (
    "Sos el asistente operacional de SmartPyme. "
    "Responde breve, claro y accionable. "
    "Usa solo el grounding provisto (summary, findings, operational_report). "
    "Si falta evidencia, dilo explicitamente y no inventes datos. "
    "No tomes decisiones automaticas ni reemplaces al runtime deterministico."
)

AssistantProvider = Callable[[dict[str, Any]], str]


class OperationalAssistantService:
    def __init__(
        self,
        *,
        provider: AssistantProvider | None = None,
        enabled: bool | None = None,
        model: str | None = None,
    ) -> None:
        self._provider = provider or self._default_provider
        self._enabled = enabled if enabled is not None else self._resolve_enabled()
        self._model = model or self._resolve_model()

    def is_enabled(self) -> bool:
        return self._enabled

    def build_response(
        self,
        *,
        user_message: str,
        summary: str,
        findings: list[dict[str, Any]],
        operational_report: dict[str, Any] | None,
    ) -> str | None:
        if not self._enabled:
            return None

        message = (user_message or "").strip()
        if not message:
            return None

        payload = {
            "model": self._model,
            "system_prompt": _DEFAULT_PROMPT,
            "user_message": message,
            "summary": summary,
            "findings": findings,
            "operational_report": operational_report or {},
        }
        try:
            response = self._provider(payload)
        except Exception:
            return None

        clean = response.strip() if isinstance(response, str) else ""
        return clean or None

    def _default_provider(self, payload: dict[str, Any]) -> str:
        api_key = (os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENCODE_API_KEY") or "").strip()
        if not api_key:
            raise ValueError("missing api key")

        base_url = (os.getenv("OPENCODE_BASE_URL") or "https://openrouter.ai/api/v1").rstrip("/")
        endpoint = f"{base_url}/chat/completions"
        request_payload = {
            "model": payload["model"],
            "messages": [
                {"role": "system", "content": payload["system_prompt"]},
                {
                    "role": "user",
                    "content": (
                        "Mensaje usuario:\n"
                        f"{payload['user_message']}\n\n"
                        "Summary:\n"
                        f"{payload['summary']}\n\n"
                        "Findings:\n"
                        f"{json.dumps(payload['findings'], ensure_ascii=True)}\n\n"
                        "Operational report:\n"
                        f"{json.dumps(payload['operational_report'], ensure_ascii=True)}"
                    ),
                },
            ],
            "temperature": 0.1,
            "max_tokens": 180,
        }
        request_data = json.dumps(request_payload).encode("utf-8")
        request = urllib_request.Request(
            endpoint,
            data=request_data,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://smartpyme.local",
                "X-Title": "SmartPyme Telegram Assistant",
            },
        )

        try:
            with urllib_request.urlopen(request, timeout=20.0) as response:
                raw = response.read().decode("utf-8")
        except (HTTPError, URLError) as exc:
            raise RuntimeError("assistant provider request failed") from exc

        data = json.loads(raw)
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("invalid provider response")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise ValueError("empty provider content")
        return content

    @staticmethod
    def _resolve_enabled() -> bool:
        return (os.getenv("ENABLE_LLM_ASSISTANT") or "").strip().lower() == "true"

    @staticmethod
    def _resolve_model() -> str:
        configured = (os.getenv("OPENCODE_MODEL") or "").strip()
        if configured:
            return configured
        return DEFAULT_FREE_MODELS[0]
