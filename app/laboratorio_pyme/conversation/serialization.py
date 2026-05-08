"""Serialización/deserialización pura de ConversationState.

Produce y consume dicts JSON-compatibles (str, int, float, list, dict, None).
Sin pickle. Sin dependencias externas. Sin Supabase.

Uso típico:
    data = conversation_state_to_dict(state)          # → dict JSON-compatible
    state = conversation_state_from_dict(data)        # → ConversationState
    json.dumps(data)                                  # siempre funciona
"""

from __future__ import annotations

from typing import Any

from app.laboratorio_pyme.conversation.state import (
    ConversationState,
    FaseConversacion,
    HipotesisActiva,
    crear_anamnesis_contexto_inicial,
)


# ---------------------------------------------------------------------------
# Serialización
# ---------------------------------------------------------------------------

def _hipotesis_to_dict(h: HipotesisActiva) -> dict[str, Any]:
    return {
        "codigo": h.codigo,
        "nombre": h.nombre,
        "peso": h.peso,
        "dimension": h.dimension,
        "evidencia_faltante": list(h.evidencia_faltante),
        "evidencia_confirmada": list(h.evidencia_confirmada),
        "subsistemas_afectados": list(h.subsistemas_afectados),
    }


def conversation_state_to_dict(state: ConversationState) -> dict[str, Any]:
    """Convierte un ConversationState a un dict JSON-compatible.

    Todos los valores son tipos primitivos de Python (str, float, list, dict, None).
    Apto para almacenar en JSONB, Redis, archivo o cualquier store.
    """
    return {
        "cliente_id": state.cliente_id,
        "fase": state.fase.value,
        "dolor_principal": state.dolor_principal,
        "dimension_foco": state.dimension_foco,
        "ultima_pregunta": state.ultima_pregunta,
        "historial_mensajes": list(state.historial_mensajes),
        "historial_preguntas": list(state.historial_preguntas),
        "evidencia_requerida": list(state.evidencia_requerida),
        "evidencia_confirmada": list(state.evidencia_confirmada),
        "datos_conocidos": [dict(d) for d in state.datos_conocidos],
        "incertidumbres": list(state.incertidumbres),
        "anamnesis_contexto": {
            "rubro": state.anamnesis_contexto.get("rubro"),
            "tamano_aprox": state.anamnesis_contexto.get("tamano_aprox"),
            "urgencia": state.anamnesis_contexto.get("urgencia"),
            "impacto_economico_estimado": state.anamnesis_contexto.get("impacto_economico_estimado"),
            "impacto_tiempo": state.anamnesis_contexto.get("impacto_tiempo"),
            "proceso_afectado": state.anamnesis_contexto.get("proceso_afectado"),
            "periodo_problema": state.anamnesis_contexto.get("periodo_problema"),
            "evidencia_disponible": list(
                state.anamnesis_contexto.get("evidencia_disponible") or []
            ),
        },
        "hipotesis_activas": [_hipotesis_to_dict(h) for h in state.hipotesis_activas],
    }


# ---------------------------------------------------------------------------
# Deserialización
# ---------------------------------------------------------------------------

def _hipotesis_from_dict(data: dict[str, Any]) -> HipotesisActiva:
    return HipotesisActiva(
        codigo=data["codigo"],
        nombre=data["nombre"],
        peso=float(data["peso"]),
        dimension=data["dimension"],
        evidencia_faltante=list(data.get("evidencia_faltante") or []),
        evidencia_confirmada=list(data.get("evidencia_confirmada") or []),
        subsistemas_afectados=list(data.get("subsistemas_afectados") or []),
    )


def conversation_state_from_dict(data: dict[str, Any]) -> ConversationState:
    """Reconstruye un ConversationState desde un dict.

    - Si falta un campo opcional, usa el default sano del dataclass.
    - Si fase viene como string, lo convierte a FaseConversacion.
    - Nunca lanza KeyError por campos opcionales ausentes.
    """
    fase_raw = data.get("fase", FaseConversacion.ANAMNESIS_GENERAL.value)
    if isinstance(fase_raw, str):
        fase = FaseConversacion(fase_raw)
    else:
        fase = FaseConversacion(fase_raw.value)

    hipotesis_raw = data.get("hipotesis_activas") or []
    hipotesis_activas = [_hipotesis_from_dict(h) for h in hipotesis_raw]
    contexto_raw = data.get("anamnesis_contexto") or {}
    contexto = crear_anamnesis_contexto_inicial()
    if isinstance(contexto_raw, dict):
        for key in (
            "rubro",
            "tamano_aprox",
            "urgencia",
            "impacto_economico_estimado",
            "impacto_tiempo",
            "proceso_afectado",
            "periodo_problema",
        ):
            value = contexto_raw.get(key)
            if isinstance(value, str):
                contexto[key] = value
            elif value is None:
                contexto[key] = None
        evidencia = contexto_raw.get("evidencia_disponible")
        if isinstance(evidencia, list):
            contexto["evidencia_disponible"] = [v for v in evidencia if isinstance(v, str)]

    return ConversationState(
        cliente_id=data["cliente_id"],
        fase=fase,
        dolor_principal=data.get("dolor_principal"),
        dimension_foco=data.get("dimension_foco"),
        ultima_pregunta=data.get("ultima_pregunta"),
        historial_mensajes=list(data.get("historial_mensajes") or []),
        historial_preguntas=list(data.get("historial_preguntas") or []),
        evidencia_requerida=list(data.get("evidencia_requerida") or []),
        evidencia_confirmada=list(data.get("evidencia_confirmada") or []),
        datos_conocidos=list(data.get("datos_conocidos") or []),
        incertidumbres=list(data.get("incertidumbres") or []),
        anamnesis_contexto=contexto,
        hipotesis_activas=hipotesis_activas,
    )
