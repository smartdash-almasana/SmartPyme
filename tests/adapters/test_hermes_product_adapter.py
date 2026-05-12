from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.adapters.hermes_product_adapter import HermesProductAdapter


@pytest.fixture
def mock_hermes_runtime():
    """Crea un mock del runtime de Hermes para inyección."""
    runtime = MagicMock()
    runtime.run.return_value = "Respuesta desde el runtime mockeado."
    return runtime


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
