"""Tests del ciclo conversacional mínimo de TelegramAdapter con anamnesis.

Verifica que un mensaje con señal operacional:
- Devuelve status ok
- Devuelve mode anamnesis_inicial
- Incluye message de anamnesis
- Incluye anamnesis serializada (dict)
- Incluye laboratorio serializado (dict)
- NO llama a owner_status_provider (no cae al fallback Hermes)
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.adapters.telegram_adapter import TelegramAdapter
from app.services.initial_laboratory_anamnesis_service import (
    AnamnesisOriginaria,
    InitialLaboratoryAnamnesisResult,
    InitialLaboratoryAnamnesisService,
    LaboratorioInicialContrato,
)

CLIENTE_ID = "cliente-test-001"
TELEGRAM_USER_ID = 42
CLAIM_CON_SENAL = "vendo mucho pero no queda plata"
CLAIM_SIN_SENAL = "hola, cómo estás?"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_update(text: str, user_id: int = TELEGRAM_USER_ID) -> dict:
    """Construye un update dict mínimo de Telegram."""
    return {
        "message": {
            "from": {"id": user_id},
            "text": text,
        }
    }


def _make_identity_service(cliente_id: str = CLIENTE_ID) -> MagicMock:
    """Identity service que siempre devuelve el cliente_id dado."""
    svc = MagicMock()
    svc.get_cliente_id_for_telegram_user.return_value = cliente_id
    return svc


def _make_anamnesis_result() -> InitialLaboratoryAnamnesisResult:
    """Resultado de anamnesis mínimo para inyección en mocks."""
    anamnesis = AnamnesisOriginaria(
        tenant_id=CLIENTE_ID,
        canal="telegram",
        frases_textuales=[CLAIM_CON_SENAL],
        dolores_detectados=["incertidumbre de rentabilidad"],
        hipotesis_iniciales=["Tensión de caja", "Margen erosionado"],
        taxonomia_inicial={"rubro": None, "tipo_pyme": None},
        documentos_pedidos=["ventas del período", "costos"],
        estado_conversacional="esperando_documentacion",
    )
    laboratorio = LaboratorioInicialContrato(
        tenant_id=CLIENTE_ID,
        estado_conversacional="esperando_documentacion",
        hipotesis_a_contrastar=["Tensión de caja", "Margen erosionado"],
        evidencia_requerida=["ventas del período", "costos"],
        capability="laboratorio_inicial_margen_rentabilidad",
        tipo_documental_esperado=["xlsx", "csv"],
        campos_esperados=["producto", "fecha", "precio_venta", "costo"],
        nivel_confianza="hipotesis_abierta",
        limite_actual="No se puede afirmar rentabilidad real sin evidencia.",
    )
    return InitialLaboratoryAnamnesisResult(
        message="Entiendo el dolor: estás vendiendo pero no tenés claridad sobre si ganás plata.",
        anamnesis=anamnesis,
        laboratorio=laboratorio,
    )


# ---------------------------------------------------------------------------
# Tests principales
# ---------------------------------------------------------------------------

class TestTelegramAdapterAnamnesisConversacional:
    """Ciclo conversacional mínimo: anamnesis antes del fallback Hermes."""

    def test_mensaje_con_senal_devuelve_status_ok(self):
        """Un mensaje con señal operacional devuelve status ok."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
        )

        result = adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        assert result["status"] == "ok"

    def test_mensaje_con_senal_devuelve_mode_anamnesis_inicial(self):
        """Un mensaje con señal operacional devuelve mode anamnesis_inicial."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
        )

        result = adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        assert result["mode"] == "anamnesis_inicial"

    def test_mensaje_con_senal_incluye_message_de_anamnesis(self):
        """El campo message contiene el texto de anamnesis."""
        expected_message = "Entiendo el dolor: estás vendiendo pero no tenés claridad sobre si ganás plata."
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
        )

        result = adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        assert result["message"] == expected_message

    def test_mensaje_con_senal_incluye_anamnesis_serializada(self):
        """El resultado incluye anamnesis como dict serializado."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
        )

        result = adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        assert "anamnesis" in result
        assert isinstance(result["anamnesis"], dict)
        assert result["anamnesis"]["tenant_id"] == CLIENTE_ID
        assert result["anamnesis"]["canal"] == "telegram"
        assert isinstance(result["anamnesis"]["hipotesis_iniciales"], list)

    def test_mensaje_con_senal_incluye_laboratorio_serializado(self):
        """El resultado incluye laboratorio como dict serializado."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
        )

        result = adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        assert "laboratorio" in result
        assert isinstance(result["laboratorio"], dict)
        assert result["laboratorio"]["tenant_id"] == CLIENTE_ID
        assert isinstance(result["laboratorio"]["evidencia_requerida"], list)

    def test_mensaje_con_senal_no_llama_owner_status(self):
        """Cuando anamnesis responde, NO se llama a owner_status_provider."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()
        owner_status_spy = MagicMock(return_value={})

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
            owner_status_provider=owner_status_spy,
        )

        adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        owner_status_spy.assert_not_called()

    def test_mensaje_con_senal_incluye_cliente_id_correcto(self):
        """El resultado incluye el cliente_id del usuario autenticado."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(CLIENTE_ID),
            anamnesis_service=anamnesis_svc,
        )

        result = adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        assert result["cliente_id"] == CLIENTE_ID

    def test_anamnesis_recibe_tenant_id_y_canal_correctos(self):
        """El servicio de anamnesis recibe tenant_id=cliente_id y channel=telegram."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = _make_anamnesis_result()

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(CLIENTE_ID),
            anamnesis_service=anamnesis_svc,
        )

        adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        anamnesis_svc.process.assert_called_once_with(
            tenant_id=CLIENTE_ID,
            channel="telegram",
            text=CLAIM_CON_SENAL,
        )


# ---------------------------------------------------------------------------
# Tests de fallback: sin señal → Hermes
# ---------------------------------------------------------------------------

class TestTelegramAdapterFallbackHermes:
    """Cuando anamnesis devuelve None, el flujo cae al fallback Hermes."""

    def test_mensaje_sin_senal_no_usa_anamnesis_mode(self):
        """Un mensaje sin señal operacional no devuelve mode anamnesis_inicial."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = None  # sin señal

        hermes_adapter = MagicMock()
        hermes_adapter.get_assistant_response.return_value = "Respuesta Hermes."
        owner_status = MagicMock(return_value={"findings": [], "operational_report": {}})

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
            hermes_product_adapter=hermes_adapter,
            owner_status_provider=owner_status,
        )

        result = adapter.handle_update(_make_update(CLAIM_SIN_SENAL))

        assert result.get("mode") != "anamnesis_inicial"

    def test_mensaje_sin_senal_llama_owner_status_para_hermes(self):
        """Cuando anamnesis devuelve None, se llama a owner_status_provider para Hermes."""
        anamnesis_svc = MagicMock(spec=InitialLaboratoryAnamnesisService)
        anamnesis_svc.process.return_value = None

        hermes_adapter = MagicMock()
        hermes_adapter.get_assistant_response.return_value = "Respuesta Hermes."
        owner_status_spy = MagicMock(return_value={"findings": [], "operational_report": {}})

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            anamnesis_service=anamnesis_svc,
            hermes_product_adapter=hermes_adapter,
            owner_status_provider=owner_status_spy,
        )

        adapter.handle_update(_make_update(CLAIM_SIN_SENAL))

        owner_status_spy.assert_called_once_with(CLIENTE_ID)


# ---------------------------------------------------------------------------
# Test de integración real (sin mocks de anamnesis)
# ---------------------------------------------------------------------------

class TestTelegramAdapterAnamnesisIntegracion:
    """Ciclo real con InitialLaboratoryAnamnesisService sin mockear."""

    def test_claim_real_con_senal_devuelve_anamnesis_inicial(self):
        """Integración real: claim con señal activa anamnesis sin mocks."""
        owner_status_spy = MagicMock(return_value={})

        adapter = TelegramAdapter(
            identity_service=_make_identity_service(),
            owner_status_provider=owner_status_spy,
            # anamnesis_service real (default)
        )

        result = adapter.handle_update(_make_update(CLAIM_CON_SENAL))

        assert result["status"] == "ok"
        assert result["mode"] == "anamnesis_inicial"
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0
        assert isinstance(result["anamnesis"], dict)
        assert isinstance(result["laboratorio"], dict)
        # No debe haber llamado a owner_status
        owner_status_spy.assert_not_called()
