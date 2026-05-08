"""Tests del ConversationService.

Verifica que el service orquesta correctamente repository + engine.
Usa InMemoryConversationRepository como adapter concreto.
Sin DB, sin Supabase, sin LLM.
"""

from __future__ import annotations

from app.laboratorio_pyme.conversation.in_memory_repository import (
    InMemoryConversationRepository,
)
from app.laboratorio_pyme.conversation.service import ConversationService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service() -> ConversationService:
    """Crea un service fresco con repositorio in-memory para cada test."""
    return ConversationService(InMemoryConversationRepository())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_process_message_devuelve_respuesta_del_engine():
    service = _make_service()

    result = service.process_message("cliente_svc_001", "vendo mucho pero no queda plata")

    claves_esperadas = {
        "cliente_id",
        "estado",
        "fase",
        "pregunta",
        "proxima_pregunta",
        "hipotesis_activas",
        "evidencia_requerida",
        "dimension_detectada",
        "diagnostico_emitido",
        "diagnostico_final",
    }
    assert claves_esperadas.issubset(set(result.keys()))


def test_crea_sesion_si_no_existe():
    repo = InMemoryConversationRepository()
    service = ConversationService(repo)

    # Antes del primer mensaje no hay sesión
    assert repo.get_active_session("cliente_nuevo_svc") is None

    service.process_message("cliente_nuevo_svc", "tengo problemas de caja")

    # Después del mensaje la sesión existe y está persistida
    state = repo.get_active_session("cliente_nuevo_svc")
    assert state is not None
    assert state.cliente_id == "cliente_nuevo_svc"


def test_persiste_historial_entre_mensajes():
    service = _make_service()

    service.process_message("cliente_hist_svc", "vendo mucho pero no queda plata")
    service.process_message("cliente_hist_svc", "además los costos subieron")

    # Recuperamos el state directamente del repo para inspeccionar
    repo = service._repository  # type: ignore[attr-defined]
    state = repo.get_active_session("cliente_hist_svc")

    assert state is not None
    assert len(state.historial_mensajes) == 2
    assert state.historial_mensajes[0] == "vendo mucho pero no queda plata"
    assert state.historial_mensajes[1] == "además los costos subieron"


def test_conserva_cliente_id_en_resultado():
    service = _make_service()

    result = service.process_message("cliente_id_check", "hay problemas con precios")

    assert result["cliente_id"] == "cliente_id_check"


def test_funciona_con_in_memory_repository():
    """Verifica integración explícita con InMemoryConversationRepository."""
    repo = InMemoryConversationRepository()
    service = ConversationService(repo)

    result = service.process_message("cliente_inmem", "tengo mucho stock parado")

    assert result is not None
    assert "stock_inmovilizado" in result["hipotesis_activas"]


def test_no_emite_diagnostico_definitivo():
    service = _make_service()

    result = service.process_message("cliente_nodiag", "vendo mucho pero no queda plata")

    assert result["diagnostico_emitido"] is False
    assert result["diagnostico_final"] is None


def test_hipotesis_se_acumulan_entre_mensajes():
    service = _make_service()

    r1 = service.process_message("cliente_acum", "vendo mucho pero no queda plata")
    r2 = service.process_message("cliente_acum", "tengo mucho stock parado")

    # El segundo resultado debe incluir hipótesis de ambos mensajes
    assert "stock_inmovilizado" in r2["hipotesis_activas"]
    assert any(
        h in r2["hipotesis_activas"]
        for h in ["margen_erosionado", "caja_inconsistente"]
    )


def test_preguntas_no_se_repiten_entre_turnos():
    service = _make_service()

    r1 = service.process_message("cliente_norepeat", "vendo mucho pero no queda plata")
    r2 = service.process_message("cliente_norepeat", "vendo mucho pero no queda plata")

    assert r1["pregunta"] != r2["pregunta"]
