from __future__ import annotations

from app.laboratorio_pyme.conversation.hypotheses import HIPOTESIS
from app.laboratorio_pyme.conversation.questions import generar_proxima_pregunta



def _activar_hipotesis(mensaje: str) -> list[str]:
    mensaje_lower = mensaje.lower()
    activas: list[str] = []

    for nombre, data in HIPOTESIS.items():
        if any(keyword in mensaje_lower for keyword in data["keywords"]):
            activas.append(nombre)

    return activas



def procesar_mensaje(state: dict, mensaje: str) -> dict:
    nuevas_hipotesis = _activar_hipotesis(mensaje)

    for hipotesis in nuevas_hipotesis:
        if hipotesis not in state["hipotesis_activas"]:
            state["hipotesis_activas"].append(hipotesis)

        for evidencia in HIPOTESIS[hipotesis]["evidencia"]:
            if evidencia not in state["evidencia_requerida"]:
                state["evidencia_requerida"].append(evidencia)

    if state["dolor_principal"] is None:
        state["dolor_principal"] = mensaje

    pregunta = generar_proxima_pregunta(state)

    state["ultima_pregunta"] = pregunta

    if pregunta not in state["historial_preguntas"]:
        state["historial_preguntas"].append(pregunta)

    return {
        "cliente_id": state["cliente_id"],
        "estado": state["estado"],
        "hipotesis_activas": state["hipotesis_activas"],
        "evidencia_requerida": state["evidencia_requerida"],
        "proxima_pregunta": pregunta,
        "diagnostico_final": None,
    }
