from __future__ import annotations

import os
from typing import Any

# from app.runtime.hermes_product_loader import load_product_config
# from app.runtime.hermes_smartpyme_runtime import HermesSmartPymeRuntime


class HermesProductAdapter:
    """
    Adapter para interactuar con una instancia de Hermes específica para producto.

    Esta clase es un scaffold y su implementación real (invocando a Hermes)
    se completará en un commit posterior.
    """

    def __init__(self, hermes_runtime: Any | None = None) -> None:
        """
        Inicializa el adapter.

        Permite inyectar un `hermes_runtime` mockeado para testing.
        Si no se provee runtime, el adapter falla cerrado y devuelve None.
        """
        self._hermes_runtime = hermes_runtime
        self._is_enabled = self._resolve_enabled()

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

            message = (user_message or "").strip()
            if not message:
                return None

            hermes_payload = {
                "tenant_id": tenant_id,
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

    def _initialize_runtime(self) -> Any:
        """Carga la config y prepara el runtime de Hermes. (Implementación futura)"""
        # config = load_product_config()
        # runtime = HermesSmartPymeRuntime(config["hermes_repo_path"])
        # runtime.bootstrap()
        # hermes_instance = runtime.get_agent(config["agent_config"])
        # return hermes_instance
        raise NotImplementedError("La inicialización del runtime de Hermes no está implementada.")

    @staticmethod
    def _resolve_enabled() -> bool:
        """Resuelve si la capa LLM está habilitada vía feature flag."""
        return (os.getenv("ENABLE_LLM_ASSISTANT") or "").strip().lower() == "true"
