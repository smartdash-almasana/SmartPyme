"""Factory minima para construir ConversationService sin acoplar infraestructura."""

from __future__ import annotations

from app.laboratorio_pyme.conversation.in_memory_repository import (
    InMemoryConversationRepository,
)
from app.laboratorio_pyme.conversation.ports import ConversationRepository
from app.laboratorio_pyme.conversation.service import ConversationService


def build_conversation_service(
    repository: ConversationRepository | None = None,
) -> ConversationService:
    """Construye ConversationService con repository configurable.

    - Si no se inyecta repository, usa InMemoryConversationRepository por defecto.
    - Si se inyecta repository, respeta esa instancia.
    """
    resolved_repository = repository or InMemoryConversationRepository()
    return ConversationService(resolved_repository)
