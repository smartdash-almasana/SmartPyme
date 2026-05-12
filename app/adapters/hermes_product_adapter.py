from __future__ import annotations

import os
from typing import Any

from app.runtime.hermes_product_loader import load_product_config
from app.runtime.hermes_vertex_gemma_client import VertexGemmaClient


class HermesProductRuntimeScaffold:
    """Runtime mínimo fail-closed basado en config real de Hermes Producto."""

    def __init__(
        self,
        config: dict[str, Any],
        vertex_client: VertexGemmaClient | None = None,
    ) -> None:
        self.config = config
        self._vertex_client = vertex_client or VertexGemmaClient()

    def run(self, payload: dict[str, Any]) -> str | None:
        """Intenta Vertex/Gemma controlado y preserva fallback determinístico."""
        if not self._has_required_grounding(payload):
            return None
        try:
            response = self._vertex_client.generate(payload, self.config)
        except Exception:
            return None
        clean = response.strip() if isinstance(response, str) else ""
        return clean or None

    @staticmethod
    def _has_required_grounding(payload: dict[str, Any]) -> bool:
        summary = payload.get("summary")
        findings = payload.get("findings")
        operational_report = payload.get("operational_report")
        return bool(summary or findings or operational_report)


class HermesProductAdapter:
    """
    Adapter para interactuar con una instancia de Hermes específica para producto.

    Esta clase prepara un runtime de producto de bajo privilegio, configurable,
    inyectable y fail-closed. La invocación LLM real queda detrás del runtime.
    """

    def __init__(self, hermes_runtime: Any | None = None) -> None:
        """
        Inicializa el adapter.

        Permite inyectar un `hermes_runtime` mockeado para testing.
        Si no se provee runtime, intenta cargar la config real y preparar un
        scaffold fail-closed. Ante cualquier error, no bloquea el fallback.
        """
        self._is_enabled = self._resolve_enabled()
        self._hermes_runtime = hermes_runtime
        if self._is_enabled and self._hermes_runtime is None:
            self._hermes_runtime = self._safe_initialize_runtime()

    def get_assistant_response(
        self,
        *,
        tenant_id: str,
        user_message: str,
        summary: dict,
        findings: list[dict],
        operational_report: dict,
    ) -> str | None:
        """
        Orquesta una instancia de Hermes-Producto para generar una respuesta.

        Retorna la respuesta como string o None si Hermes falla, está deshabilitado
        o no responde, permitiendo el fallback determinístico.
        """
        if not self._is_enabled:
            return None

        try:
            if self._hermes_runtime is None:
                return None

            tenant = (tenant_id or "").strip()
            message = (user_message or "").strip()
            if not tenant or not message:
                return None

            hermes_payload = {
                "tenant_id": tenant,
                "user_message": message,
                "summary": summary,
                "findings": findings,
                "operational_report": operational_report,
            }

            response = self._hermes_runtime.run(hermes_payload)
            clean = response.strip() if isinstance(response, str) else ""
            return clean or None

        except Exception:
            # Captura cualquier error durante la inicialización o ejecución
            # y devuelve None para asegurar el fallback determinístico.
            return None

    def _safe_initialize_runtime(self) -> Any | None:
        try:
            return self._initialize_runtime()
        except Exception:
            return None

    def _initialize_runtime(self) -> Any:
        """Carga la config real y prepara el scaffold mínimo de Hermes Producto."""
        config = load_product_config()
        return HermesProductRuntimeScaffold(config)

    @staticmethod
    def _resolve_enabled() -> bool:
        """Resuelve si la capa LLM está habilitada vía feature flag."""
        return (os.getenv("ENABLE_LLM_ASSISTANT") or "").strip().lower() == "true"
