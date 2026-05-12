from __future__ import annotations

from app.services.operational_assistant_service import OperationalAssistantService


def test_returns_none_when_feature_flag_disabled():
    service = OperationalAssistantService(enabled=False, provider=lambda _: "unused")

    result = service.build_response(
        user_message="que significa este hallazgo?",
        summary="jobs=1",
        findings=[{"finding_type": "VENTA_BAJO_COSTO"}],
        operational_report={"risk_level": "alto"},
    )

    assert result is None


def test_build_response_with_mock_provider_receives_grounding_payload():
    captured = {}

    def fake_provider(payload):
        captured.update(payload)
        return "Significa que vendes por debajo del costo. Revisa precios y margen."

    service = OperationalAssistantService(
        enabled=True, provider=fake_provider, model="gemma-4"
    )

    result = service.build_response(
        user_message="que hago con este finding?",
        summary=(
            "Estado SmartPyme para pyme_A: jobs=1, hallazgos=1, "
            "formulas=0, patologias=0."
        ),
        findings=[{"finding_type": "VENTA_BAJO_COSTO", "difference": -200.0}],
        operational_report={"status": "active"},
    )

    assert result is not None
    assert "vendes por debajo del costo" in result
    assert captured["model"] == "gemma-4"
    assert captured["user_message"] == "que hago con este finding?"
    assert captured["findings"][0]["finding_type"] == "VENTA_BAJO_COSTO"


def test_fallback_none_when_provider_fails():
    def failing_provider(_payload):
        raise RuntimeError("network down")

    service = OperationalAssistantService(enabled=True, provider=failing_provider)

    result = service.build_response(
        user_message="por que paso?",
        summary="summary",
        findings=[],
        operational_report={},
    )

    assert result is None


def test_enabled_invalid_empty_response_returns_none():
    service = OperationalAssistantService(enabled=True, provider=lambda _: "   ")

    result = service.build_response(
        user_message="como mejorar?",
        summary="summary",
        findings=[],
        operational_report={},
    )

    assert result is None
