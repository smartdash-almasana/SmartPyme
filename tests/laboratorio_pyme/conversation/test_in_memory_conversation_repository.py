"""Tests del InMemoryConversationRepository.

Verifica el contrato del port y el aislamiento de referencias mutables.
Sin DB, sin Supabase.
"""

from __future__ import annotations

from app.laboratorio_pyme.conversation.engine import procesar_mensaje
from app.laboratorio_pyme.conversation.in_memory_repository import (
    InMemoryConversationRepository,
)
from app.laboratorio_pyme.conversation.state import (
    ConversationState,
    FaseConversacion,
    crear_estado_inicial,
)


# ---------------------------------------------------------------------------
# Tests del contrato básico
# ---------------------------------------------------------------------------

def test_get_active_session_devuelve_none_si_no_existe():
    repo = InMemoryConversationRepository()

    resultado = repo.get_active_session("cliente_inexistente")

    assert resultado is None


def test_get_or_create_crea_sesion_nueva():
    repo = InMemoryConversationRepository()

    state = repo.get_or_create_active_session("cliente_nuevo")

    assert state is not None
    assert isinstance(state, ConversationState)
    assert state.cliente_id == "cliente_nuevo"
    assert state.fase == FaseConversacion.ANAMNESIS_GENERAL
    assert state.hipotesis_activas == []


def test_get_or_create_reutiliza_sesion_guardada():
    repo = InMemoryConversationRepository()

    # Primera llamada: crea
    state_1 = repo.get_or_create_active_session("cliente_reutiliza")
    procesar_mensaje(state_1, "vendo mucho pero no queda plata")
    repo.save_active_session(state_1)

    # Segunda llamada: debe devolver la sesión guardada
    state_2 = repo.get_or_create_active_session("cliente_reutiliza")

    assert state_2.cliente_id == "cliente_reutiliza"
    assert state_2.dolor_principal == "vendo mucho pero no queda plata"
    assert len(state_2.hipotesis_activas) > 0


def test_save_persiste_cambios():
    repo = InMemoryConversationRepository()

    state = crear_estado_inicial("cliente_save")
    procesar_mensaje(state, "tengo mucho stock parado")
    repo.save_active_session(state)

    recuperado = repo.get_active_session("cliente_save")

    assert recuperado is not None
    assert recuperado.dolor_principal == "tengo mucho stock parado"
    assert any(h.codigo == "stock_inmovilizado" for h in recuperado.hipotesis_activas)


def test_save_es_idempotente():
    repo = InMemoryConversationRepository()

    state = crear_estado_inicial("cliente_idempotente")
    repo.save_active_session(state)
    repo.save_active_session(state)  # segunda llamada no debe duplicar ni lanzar

    recuperado = repo.get_active_session("cliente_idempotente")
    assert recuperado is not None
    assert recuperado.cliente_id == "cliente_idempotente"


def test_clientes_aislados():
    repo = InMemoryConversationRepository()

    state_a = crear_estado_inicial("cliente_a")
    procesar_mensaje(state_a, "vendo mucho pero no queda plata")
    repo.save_active_session(state_a)

    state_b = repo.get_or_create_active_session("cliente_b")

    # cliente_b no debe ver datos de cliente_a
    assert state_b.hipotesis_activas == []
    assert state_b.dolor_principal is None

    # cliente_a sigue intacto
    recuperado_a = repo.get_active_session("cliente_a")
    assert recuperado_a is not None
    assert len(recuperado_a.hipotesis_activas) > 0


# ---------------------------------------------------------------------------
# Tests de aislamiento de referencias mutables
# ---------------------------------------------------------------------------

def test_no_comparte_referencia_mutable_en_get_active_session():
    repo = InMemoryConversationRepository()

    state_original = crear_estado_inicial("cliente_ref")
    state_original.dolor_principal = "problema inicial"
    repo.save_active_session(state_original)

    # Obtenemos una copia y la mutamos SIN guardar
    copia = repo.get_active_session("cliente_ref")
    assert copia is not None
    copia.dolor_principal = "mutación no guardada"

    # El store no debe haber cambiado
    desde_store = repo.get_active_session("cliente_ref")
    assert desde_store is not None
    assert desde_store.dolor_principal == "problema inicial"


def test_no_comparte_referencia_mutable_en_get_or_create():
    repo = InMemoryConversationRepository()

    copia_1 = repo.get_or_create_active_session("cliente_ref2")
    copia_1.dolor_principal = "mutación sin save"

    # Segunda llamada debe devolver el estado original (sin la mutación)
    copia_2 = repo.get_or_create_active_session("cliente_ref2")
    assert copia_2.dolor_principal is None


def test_save_reemplaza_estado_previo():
    repo = InMemoryConversationRepository()

    state_v1 = crear_estado_inicial("cliente_replace")
    state_v1.dolor_principal = "versión 1"
    repo.save_active_session(state_v1)

    state_v2 = crear_estado_inicial("cliente_replace")
    state_v2.dolor_principal = "versión 2"
    repo.save_active_session(state_v2)

    recuperado = repo.get_active_session("cliente_replace")
    assert recuperado is not None
    assert recuperado.dolor_principal == "versión 2"
