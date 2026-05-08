"""Adapter Supabase minimo para ConversationRepository (P0 snapshot).

Implementa persistencia en `conversation_sessions` usando una sola fila por `cliente_id`
y `state_snapshot` como JSONB serializado.
No contiene logica clinica.
"""

from __future__ import annotations

from typing import Any

from app.laboratorio_pyme.conversation.ports import ConversationRepository
from app.laboratorio_pyme.conversation.serialization import (
    conversation_state_from_dict,
    conversation_state_to_dict,
)
from app.laboratorio_pyme.conversation.state import ConversationState, crear_estado_inicial


class SupabaseConversationRepository(ConversationRepository):
    """Repositorio conversacional P0 basado en tabla `conversation_sessions`."""

    TABLE_NAME = "conversation_sessions"

    def __init__(self, supabase_client: Any) -> None:
        self._client = supabase_client

    def _validate_cliente_id(self, cliente_id: str) -> str:
        if not isinstance(cliente_id, str) or not cliente_id.strip():
            raise ValueError("cliente_id must be a non-empty string")
        return cliente_id.strip()

    def _row_to_state(self, row: dict[str, Any]) -> ConversationState:
        snapshot = row.get("state_snapshot") or {}
        if not isinstance(snapshot, dict):
            raise ValueError("state_snapshot must be a dict-compatible object")
        return conversation_state_from_dict(snapshot)

    def get_active_session(self, cliente_id: str) -> ConversationState | None:
        cliente_id_normalizado = self._validate_cliente_id(cliente_id)
        response = (
            self._client.table(self.TABLE_NAME)
            .select("*")
            .eq("cliente_id", cliente_id_normalizado)
            .limit(1)
            .execute()
        )
        data = getattr(response, "data", None)
        if not data:
            return None
        row = data[0] if isinstance(data, list) else data
        if not isinstance(row, dict):
            raise ValueError("Supabase response row must be a dict")
        return self._row_to_state(row)

    def get_or_create_active_session(self, cliente_id: str) -> ConversationState:
        cliente_id_normalizado = self._validate_cliente_id(cliente_id)
        existing = self.get_active_session(cliente_id_normalizado)
        if existing is not None:
            return existing

        nuevo = crear_estado_inicial(cliente_id_normalizado)
        self.save_active_session(nuevo)
        return nuevo

    def save_active_session(self, state: ConversationState) -> None:
        cliente_id_normalizado = self._validate_cliente_id(state.cliente_id)

        state_dict = conversation_state_to_dict(state)
        state_dict["cliente_id"] = cliente_id_normalizado

        payload = {
            "cliente_id": cliente_id_normalizado,
            "fase": state.fase.value,
            "dolor_principal": state.dolor_principal,
            "dimension_foco": state.dimension_foco,
            "ultima_pregunta": state.ultima_pregunta,
            "state_snapshot": state_dict,
        }

        self._client.table(self.TABLE_NAME).upsert(payload, on_conflict="cliente_id").execute()
