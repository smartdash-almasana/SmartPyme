from __future__ import annotations

from app.laboratorio_pyme.conversation.factory import build_conversation_service
from app.laboratorio_pyme.conversation.in_memory_repository import (
    InMemoryConversationRepository,
)
from app.laboratorio_pyme.conversation.ports import ConversationRepository
from app.laboratorio_pyme.conversation.state import ConversationState, crear_estado_inicial


class _FakeRepository(ConversationRepository):
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


def test_build_conversation_service_devuelve_service_funcional() -> None:
    service = build_conversation_service()

    result = service.process_message("cliente_factory_001", "vendo mucho pero no queda plata")

    assert result["cliente_id"] == "cliente_factory_001"
    assert "pregunta" in result


def test_factory_default_in_memory_persiste_historial_entre_mensajes() -> None:
    service = build_conversation_service()

    service.process_message("cliente_factory_hist", "vendo mucho pero no queda plata")
    service.process_message("cliente_factory_hist", "ademas subi precios")

    repo = service._repository  # type: ignore[attr-defined]
    state = repo.get_active_session("cliente_factory_hist")

    assert state is not None
    assert len(state.historial_mensajes) == 2
    assert state.historial_mensajes[0] == "vendo mucho pero no queda plata"
    assert state.historial_mensajes[1] == "ademas subi precios"


def test_build_conversation_service_usa_repository_inyectado() -> None:
    custom_repo = _FakeRepository()
    service = build_conversation_service(custom_repo)

    service.process_message("cliente_factory_custom", "tengo mucho stock parado")

    persisted = custom_repo.get_active_session("cliente_factory_custom")
    assert persisted is not None
    assert persisted.cliente_id == "cliente_factory_custom"
    assert len(persisted.historial_mensajes) == 1


def test_factory_default_no_requiere_supabase_ni_env_vars() -> None:
    service = build_conversation_service()

    repo = service._repository  # type: ignore[attr-defined]
    assert isinstance(repo, InMemoryConversationRepository)
