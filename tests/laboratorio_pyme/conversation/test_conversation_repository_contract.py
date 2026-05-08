"""Tests del contrato ConversationRepository usando un fake in-memory.

Valida que cualquier implementación concreta del port se comporte
correctamente sin tocar Supabase, DB ni el engine.
"""

from __future__ import annotations

from app.laboratorio_pyme.conversation.engine import procesar_mensaje
from app.laboratorio_pyme.conversation.ports import ConversationRepository
from app.laboratorio_pyme.conversation.state import (
    ConversationState,
    crear_estado_inicial,
)


# ---------------------------------------------------------------------------
# Fake in-memory — implementación mínima del contrato para tests
# ---------------------------------------------------------------------------

class FakeConversationRepository(ConversationRepository):
    """Implementación en memoria del port. Solo para tests."""

    def __init__(self) -> None:
        self._store: dict[str, ConversationState] = {}

    def get_active_session(self, cliente_id: str) -> ConversationState | None:
        return self._store.get(cliente_id)

    def get_or_create_active_session(self, cliente_id: str) -> ConversationState:
        if cliente_id not in self._store:
            self._store[cliente_id] = crear_estado_inicial(cliente_id)
        return self._store[cliente_id]

    def save_active_session(self, state: ConversationState) -> None:
        self._store[state.cliente_id] = state


# ---------------------------------------------------------------------------
# Tests del contrato
# ---------------------------------------------------------------------------

def test_get_active_session_devuelve_none_si_no_existe():
    repo = FakeConversationRepository()

    resultado = repo.get_active_session("cliente_inexistente")

    assert resultado is None


def test_get_or_create_crea_sesion_nueva():
    repo = FakeConversationRepository()

    state = repo.get_or_create_active_session("cliente_nuevo")

    assert state is not None
    assert isinstance(state, ConversationState)
    assert state.cliente_id == "cliente_nuevo"


def test_get_or_create_reutiliza_sesion_existente():
    repo = FakeConversationRepository()

    state_1 = repo.get_or_create_active_session("cliente_reutiliza")
    # Mutamos el estado para verificar que se reutiliza el mismo objeto
    state_1.dolor_principal = "problema de caja"

    state_2 = repo.get_or_create_active_session("cliente_reutiliza")

    assert state_2 is state_1
    assert state_2.dolor_principal == "problema de caja"


def test_save_persiste_cambios_del_state():
    repo = FakeConversationRepository()

    state = crear_estado_inicial("cliente_save")
    procesar_mensaje(state, "vendo mucho pero no queda plata")
    repo.save_active_session(state)

    recuperado = repo.get_active_session("cliente_save")

    assert recuperado is not None
    assert recuperado.cliente_id == "cliente_save"
    assert len(recuperado.hipotesis_activas) > 0
    assert recuperado.dolor_principal == "vendo mucho pero no queda plata"


def test_cliente_id_aislado_entre_clientes():
    repo = FakeConversationRepository()

    state_a = repo.get_or_create_active_session("cliente_a")
    procesar_mensaje(state_a, "tengo mucho stock parado")
    repo.save_active_session(state_a)

    state_b = repo.get_or_create_active_session("cliente_b")

    # cliente_b no debe ver hipótesis de cliente_a
    assert state_b.hipotesis_activas == []
    assert state_b.dolor_principal is None

    recuperado_a = repo.get_active_session("cliente_a")
    assert recuperado_a is not None
    assert any(h.codigo == "stock_inmovilizado" for h in recuperado_a.hipotesis_activas)
