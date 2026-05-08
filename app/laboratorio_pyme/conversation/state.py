from __future__ import annotations

from typing import Any

ConversationState = dict[str, Any]


def crear_estado_inicial(cliente_id: str) -> ConversationState:
    return {
        "cliente_id": cliente_id,
        "estado": "anamnesis_general",
        "dolor_principal": None,
        "hipotesis_activas": [],
        "evidencia_requerida": [],
        "datos_conocidos": [],
        "incertidumbres": [],
        "historial_preguntas": [],
        "ultima_pregunta": None,
    }
