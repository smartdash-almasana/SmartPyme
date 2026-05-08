"""Servicio conversacional clínico SmartPyme.

Orquesta repository + engine en un único punto de entrada.
No contiene lógica clínica: delega todo al engine.
No usa LLM, Supabase ni endpoints.

Uso típico:
    repo = InMemoryConversationRepository()
    service = ConversationService(repo)
    result = service.process_message("cliente_001", "vendo pero no queda plata")
"""

from __future__ import annotations

from app.laboratorio_pyme.conversation.engine import procesar_mensaje
from app.laboratorio_pyme.conversation.ports import ConversationRepository


class ConversationService:
    """Orquestador mínimo: repository → engine → repository → result.

    Recibe cualquier implementación de ConversationRepository (in-memory,
    Supabase, SQL) sin acoplarse a ninguna concreta.
    """

    def __init__(self, repository: ConversationRepository) -> None:
        self._repository = repository

    def process_message(self, cliente_id: str, mensaje: str) -> dict:
        """Procesa un mensaje del cliente y persiste el estado resultante.

        Flujo:
            1. Carga o crea la sesión activa del cliente.
            2. Delega el procesamiento al engine clínico.
            3. Persiste el estado mutado por el engine.
            4. Devuelve el resultado del engine sin modificarlo.

        No emite diagnóstico definitivo. No agrega lógica clínica.
        """
        state = self._repository.get_or_create_active_session(cliente_id)
        result = procesar_mensaje(state, mensaje)
        self._repository.save_active_session(state)
        return result
