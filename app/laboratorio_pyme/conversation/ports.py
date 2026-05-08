"""Puerto de persistencia para la capa conversacional clínica SmartPyme.

Define el contrato abstracto que cualquier adapter de persistencia debe cumplir.
No contiene lógica concreta ni dependencias externas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.laboratorio_pyme.conversation.state import ConversationState


class ConversationRepository(ABC):
    """Contrato de persistencia para sesiones conversacionales clínicas.

    Implementaciones concretas (Supabase, memoria, SQL) deben heredar esta clase
    y proveer los tres métodos. El engine nunca importa un adapter directamente.
    """

    @abstractmethod
    def get_or_create_active_session(self, cliente_id: str) -> ConversationState:
        """Devuelve la sesión activa del cliente o crea una nueva si no existe.

        Garantiza que siempre se retorna un ConversationState válido.
        La sesión nueva parte de crear_estado_inicial(cliente_id).
        """
        ...

    @abstractmethod
    def get_active_session(self, cliente_id: str) -> ConversationState | None:
        """Devuelve la sesión activa del cliente, o None si no existe."""
        ...

    @abstractmethod
    def save_active_session(self, state: ConversationState) -> None:
        """Persiste el estado completo de la sesión activa.

        Debe ser idempotente: llamar dos veces con el mismo estado
        no debe producir duplicados ni errores.
        """
        ...
