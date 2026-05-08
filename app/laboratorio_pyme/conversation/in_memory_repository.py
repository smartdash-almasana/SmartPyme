"""Adapter in-memory de ConversationRepository.

Implementación concreta del port para uso en tests, desarrollo local
y cualquier contexto donde no se necesite persistencia real.

Garantías:
- Cada llamada a get_active_session / get_or_create devuelve una copia
  deserializada, no la referencia interna. Modificar el objeto devuelto
  no altera el storage hasta llamar save_active_session().
- Aislamiento total entre cliente_id distintos.
- Sin DB, sin Supabase, sin dependencias externas.
"""

from __future__ import annotations

from typing import Any

from app.laboratorio_pyme.conversation.ports import ConversationRepository
from app.laboratorio_pyme.conversation.serialization import (
    conversation_state_from_dict,
    conversation_state_to_dict,
)
from app.laboratorio_pyme.conversation.state import (
    ConversationState,
    crear_estado_inicial,
)


class InMemoryConversationRepository(ConversationRepository):
    """Repositorio conversacional en memoria.

    El storage interno guarda dicts serializados, no objetos vivos.
    Esto garantiza que cada lectura devuelve una copia independiente
    y que save_active_session() es el único punto de escritura.
    """

    def __init__(self) -> None:
        # Almacena dicts JSON-compatibles, no ConversationState directamente.
        self._store: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _load(self, cliente_id: str) -> ConversationState | None:
        """Deserializa y devuelve una copia fresca desde el store."""
        data = self._store.get(cliente_id)
        if data is None:
            return None
        return conversation_state_from_dict(data)

    def _dump(self, state: ConversationState) -> None:
        """Serializa y guarda el estado en el store."""
        self._store[state.cliente_id] = conversation_state_to_dict(state)

    # ------------------------------------------------------------------
    # Implementación del port
    # ------------------------------------------------------------------

    def get_active_session(self, cliente_id: str) -> ConversationState | None:
        """Devuelve una copia del estado activo, o None si no existe."""
        return self._load(cliente_id)

    def get_or_create_active_session(self, cliente_id: str) -> ConversationState:
        """Devuelve copia del estado activo o crea uno nuevo si no existe.

        La sesión nueva se persiste automáticamente en el store.
        """
        if cliente_id not in self._store:
            nuevo = crear_estado_inicial(cliente_id)
            self._dump(nuevo)
        return self._load(cliente_id)  # type: ignore[return-value]  # siempre existe

    def save_active_session(self, state: ConversationState) -> None:
        """Persiste el estado. Idempotente: llamar dos veces no duplica."""
        self._dump(state)
