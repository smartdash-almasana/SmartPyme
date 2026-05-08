from __future__ import annotations

from app.laboratorio_pyme.conversation.hypotheses import HIPOTESIS


def generar_proxima_pregunta(state: dict) -> str:
    historial = state.get("historial_preguntas", [])

    for hipotesis in state.get("hipotesis_activas", []):
        pregunta = HIPOTESIS[hipotesis]["pregunta"]

        if pregunta not in historial:
            return pregunta

    return "Necesito más información para continuar investigando el caso."
