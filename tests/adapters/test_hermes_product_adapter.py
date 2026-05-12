from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from app.adapters.hermes_product_adapter import (
    HermesProductAdapter,
    HermesProductRuntimeScaffold,
)
from app.runtime.hermes_product_loader import HERMES_PRODUCT_CONFIG_ENV_VAR


@pytest.fixture
def mock_hermes_runtime():
    """Crea un mock del runtime de Hermes para inyección."""
    runtime = MagicMock()
    runtime.run.return_value = "Respuesta desde el runtime mockeado."
    return runtime


class FakeVertexClient:
    def __init__(self, response: str | None = "respuesta grounded") -> None:
        self.response = response
        self.calls: list[tuple[dict, dict]] = []

    def generate(self, payload: dict, config: dict) -> str | None:
        self.calls.append((payload, config))
        return self.response


class FailingVertexClient:
    def generate(self, payload: dict, config: dict) -> str | None:
        raise RuntimeError("vertex failure")


def test_adapter_returns_none_when_disabled(monkeypatch):
    """Verifica que el adapter devuelve None si el feature flag está deshabilitado."""
    monkeypatch.setenv("ENABLE_LLM_ASSISTANT", "false")
    adapter = HermesProductAdapter()  # No se le pasa runtime, no importa

    response = adapter.get_assistant_response(
        tenant_id="test-tenant",
        user_message="hola",
        summary={},
        findings=[],
        operational_report={},
    )

    assert response is None


def test_adapter_returns_mock_response_on_success(monkeypatch, mock_hermes_runtime):
    """Verifica que el adapter devuelve la respuesta del runtime mockeado."""
    monkeypatch.setenv("ENABLE_LLM_ASSISTANT", "true")
    adapter = HermesProductAdapter(hermes_runtime=mock_hermes_runtime)

    response = adapter.get_assistant_response(
        tenant_id="test-tenant",
        user_message="hola",
        summary={},
        findings=[],
        operational_report={},
    )

    assert response == "Respuesta desde el runtime mockeado."


def test_adapter_returns_none_if_runtime_fails(monkeypatch, mock_hermes_runtime):
    """Verifica que el adapter devuelve None si el método run() del runtime falla."""
    monkeypatch.setenv("ENABLE_LLM_ASSISTANT", "true")
    mock_hermes_runtime.run.side_effect = RuntimeError("Fallo del modelo")
    adapter = HermesProductAdapter(hermes_runtime=mock_hermes_runtime)

    response = adapter.get_assistant_response(
        tenant_id="test-tenant",
        user_message="hola",
        summary={},
        findings=[],
        operational_report={},
    )

    assert response is None


def test_adapter_forwards_correct_payload_to_runtime(monkeypatch, mock_hermes_runtime):
    """
    Verifica que el payload (contrato) enviado al runtime contiene todos los
    datos de grounding requeridos.
    """
    monkeypatch.setenv("ENABLE_LLM_ASSISTANT", "true")
    adapter = HermesProductAdapter(hermes_runtime=mock_hermes_runtime)

    # Datos de prueba para el grounding
    summary_data = {"key": "summary_value"}
    findings_data = [{"finding_type": "VENTA_BAJO_COSTO"}]
    report_data = {"report_key": "report_value"}

    adapter.get_assistant_response(
        tenant_id="tenant-123",
        user_message="Analiza este reporte",
        summary=summary_data,
        findings=findings_data,
        operational_report=report_data,
    )

    # Verificar que el método `run` del mock fue llamado exactamente una vez
    mock_hermes_runtime.run.assert_called_once()

    # Extraer el payload con el que fue llamado
    call_args, _ = mock_hermes_runtime.run.call_args
    payload = call_args[0]

    # Validar el contrato del payload
    assert payload["tenant_id"] == "tenant-123"
    assert payload["user_message"] == "Analiza este reporte"
    assert payload["summary"] == summary_data
    assert payload["findings"] == findings_data
    assert payload["operational_report"] == report_data


def test_adapter_bootstraps_fail_closed_runtime_from_product_config(
    monkeypatch,
    tmp_path: Path,
):
    """Verifica bootstrap mínimo desde config real sin ejecutar LLM."""
    config = {
        "version": 1,
        "profile": "hermes_product_runtime",
        "runtime": {"mode": "fail_closed_scaffold"},
        "model": {"default": "gemma-4", "temperature": 0.1},
        "tools": {"readonly_whitelist": ["findings_read"], "prohibited": ["git"]},
        "fallback": {"required": True},
    }
    config_path = tmp_path / "hermes_product.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    monkeypatch.setenv("ENABLE_LLM_ASSISTANT", "true")
    monkeypatch.setenv(HERMES_PRODUCT_CONFIG_ENV_VAR, str(config_path))

    adapter = HermesProductAdapter()

    assert adapter._hermes_runtime is not None
    assert adapter._hermes_runtime.config["model"]["default"] == "gemma-4"

    response = adapter.get_assistant_response(
        tenant_id="tenant-123",
        user_message="explicame el estado",
        summary={"text": "estado con hallazgos"},
        findings=[{"finding_type": "VENTA_BAJO_COSTO"}],
        operational_report={},
    )
    assert response is None


def test_adapter_fails_closed_when_config_is_missing(monkeypatch):
    """Verifica que la ausencia de config activa fallback determinístico."""
    monkeypatch.setenv("ENABLE_LLM_ASSISTANT", "true")
    monkeypatch.delenv(HERMES_PRODUCT_CONFIG_ENV_VAR, raising=False)

    adapter = HermesProductAdapter()

    assert adapter._hermes_runtime is None
    assert (
        adapter.get_assistant_response(
            tenant_id="tenant-123",
            user_message="hola",
            summary={"text": "estado"},
            findings=[],
            operational_report={},
        )
        is None
    )


def test_runtime_uses_vertex_client_when_enabled_and_grounded():
    client = FakeVertexClient("respuesta desde vertex fake")
    runtime = HermesProductRuntimeScaffold(
        {"vertex": {"enabled": True}},
        vertex_client=client,
    )

    response = runtime.run({"summary": {"text": "estado"}})

    assert response == "respuesta desde vertex fake"
    assert len(client.calls) == 1


def test_runtime_preserves_none_if_vertex_client_returns_empty():
    runtime = HermesProductRuntimeScaffold(
        {"vertex": {"enabled": False}},
        vertex_client=FakeVertexClient(None),
    )

    assert runtime.run({"summary": {"text": "estado"}}) is None


def test_runtime_returns_none_if_vertex_client_fails():
    runtime = HermesProductRuntimeScaffold(
        {"vertex": {"enabled": True}},
        vertex_client=FailingVertexClient(),
    )

    assert runtime.run({"summary": {"text": "estado"}}) is None
