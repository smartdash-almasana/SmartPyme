from __future__ import annotations

import os
from typing import Any


class VertexGemmaClient:
    """Cliente mínimo fail-closed para preparar invocación Vertex/Gemma."""

    def generate(self, payload: dict[str, Any], config: dict[str, Any]) -> str | None:
        """Prepara el boundary de generación sin ejecutar red todavía."""
        if not self._is_enabled(config):
            return None
        if not self._has_required_grounding(payload):
            return None
        if not self._resolve_vertex_settings(config):
            return None
        return None

    @staticmethod
    def _is_enabled(config: dict[str, Any]) -> bool:
        vertex = config.get("vertex")
        if not isinstance(vertex, dict):
            return False
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
        location = os.getenv(str(vertex.get("location_env") or ""))
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
