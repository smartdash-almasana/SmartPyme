from __future__ import annotations

import json
import os
from typing import Any


class VertexGemmaClient:
    """Cliente mínimo fail-closed para invocar Vertex/Gemma MaaS."""

    def generate(self, payload: dict[str, Any], config: dict[str, Any]) -> str | None:
        """Genera una respuesta con Vertex/Gemma o retorna None ante cualquier falla."""
        if not self._is_enabled(config):
            return None
        if not self._has_required_grounding(payload):
            return None

        settings = self._resolve_vertex_settings(config)
        if not settings:
            return None

        prompt = self._build_prompt(payload, settings.get("system_prompt"))
        if not prompt:
            return None

        return self._invoke_vertex(prompt, settings)

    @staticmethod
    def _is_enabled(config: dict[str, Any]) -> bool:
        vertex = config.get("vertex")
        if not isinstance(vertex, dict):
            return False
        enabled_env = str(vertex.get("enabled_env") or "HERMES_PRODUCT_VERTEX_ENABLED")
        enabled_override = os.getenv(enabled_env)
        if enabled_override is not None:
            return enabled_override.strip().lower() == "true"
        return vertex.get("enabled") is True

    @staticmethod
    def _has_required_grounding(payload: dict[str, Any]) -> bool:
        return bool(
            payload.get("summary")
            or payload.get("findings")
            or payload.get("operational_report")
        )

    @staticmethod
    def _resolve_vertex_settings(config: dict[str, Any]) -> dict[str, Any] | None:
        vertex = config.get("vertex")
        if not isinstance(vertex, dict):
            return None

        project_id = os.getenv(str(vertex.get("project_id_env") or ""))
        location = os.getenv(str(vertex.get("location_env") or "")) or vertex.get("location")
        model_id = os.getenv(str(vertex.get("model_id_env") or "")) or vertex.get("model_id")

        if not project_id or not location or not model_id:
            return None

        model = config.get("model")
        model_kwargs = model if isinstance(model, dict) else {}
        return {
            "project_id": project_id,
            "location": location,
            "model_id": model_id,
            "system_prompt": config.get("system_prompt"),
            "model_kwargs": {
                "temperature": model_kwargs.get("temperature"),
                "max_output_tokens": model_kwargs.get("max_output_tokens"),
            },
        }

    @staticmethod
    def _build_prompt(payload: dict[str, Any], system_prompt: Any) -> str | None:
        user_message = (payload.get("user_message") or "").strip()
        if not user_message:
            return None

        grounding = {
            "summary": payload.get("summary") or {},
            "findings": payload.get("findings") or [],
            "operational_report": payload.get("operational_report") or {},
        }
        system = str(system_prompt or "").strip()
        grounding_json = json.dumps(grounding, ensure_ascii=False, sort_keys=True)

        return (
            "<system>\n"
            f"{system}\n"
            "</system>\n\n"
            "<user>\n"
            f"{user_message}\n"
            "</user>\n\n"
            "<grounding>\n"
            f"{grounding_json}\n"
            "</grounding>"
        )

    def _invoke_vertex(self, prompt: str, settings: dict[str, Any]) -> str | None:
        try:
            import google.genai as genai
            from google.genai import types as genai_types
        except ImportError:
            return None

        try:
            client = genai.Client(
                vertexai=True,
                project=settings["project_id"],
                location=settings["location"],
            )
            model_kwargs = settings.get("model_kwargs") or {}
            response = client.models.generate_content(
                model=settings["model_id"],
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=model_kwargs.get("temperature"),
                    max_output_tokens=model_kwargs.get("max_output_tokens"),
                ),
            )
            text = getattr(response, "text", None)
            clean = text.strip() if isinstance(text, str) else ""
            return clean or None
        except Exception:
            return None
