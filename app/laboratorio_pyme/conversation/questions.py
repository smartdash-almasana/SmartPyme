"""Generador de proxima pregunta clinica SmartPyme.

Una sola pregunta por turno.
La mas informativa posible.
Nunca diagnostica: investiga.
"""

from __future__ import annotations

from app.laboratorio_pyme.conversation.hypotheses import CATALOGO
from app.laboratorio_pyme.conversation.state import ConversationState


PREGUNTAS_APERTURA = [
    "Contame, que es lo que mas te preocupa del negocio ahora mismo?",
    "Donde sentis que el negocio te esta fallando hoy?",
    "Si tuvieras que senalar un problema urgente, cual seria?",
]

PREGUNTA_DIMENSION = (
    "Para enfocarnos mejor: el problema principal hoy es de plata "
    "(margen, caja, costos) o de tiempo (todo manual, tareas repetidas)?"
)

PREGUNTA_CIERRE = (
    "Hay algo importante del negocio que todavia no me contaste?"
)

PREGUNTAS_CONTEXTO_CRITICO: dict[str, str] = {
    "rubro": "Para entender mejor el caso: en que rubro esta tu negocio?",
    "proceso_afectado": "Que proceso puntual esta mas afectado hoy (ventas, caja, stock, compras u otro)?",
    "periodo_problema": "Desde cuando notaste este problema?",
    "impacto": "Que impacto te esta generando hoy en plata o en tiempo?",
}


PREGUNTAS_EVIDENCIA: dict[str, str] = {
    "ventas_periodo": (
        "Tenes ventas del ultimo trimestre aunque sea en Excel o PDF?"
    ),
    "compras_periodo": (
        "Tenes facturas o registros de compras del mismo periodo?"
    ),
    "lista_precios_vigente": (
        "Tenes una lista de precios actual aunque este desactualizada?"
    ),
    "lista_precios_actual": (
        "Tenes una lista de precios actual aunque este desactualizada?"
    ),
    "costo_mercaderia_vendida": (
        "Sabes cuanto te costo la mercaderia vendida el ultimo mes?"
    ),
    "resumen_caja_diaria": (
        "Llevas cierre diario de caja aunque sea manual?"
    ),
    "ventas_registradas": (
        "Tenes registro de ventas del ultimo mes?"
    ),
    "egresos_registrados": (
        "Registras pagos, gastos y egresos del negocio?"
    ),
    "inventario_actual": (
        "Tenes inventario actualizado del stock actual?"
    ),
    "ultimas_ventas_por_producto": (
        "Podes ver que productos tuvieron movimiento recientemente?"
    ),
    "fecha_ultima_compra_por_item": (
        "Sabes cuando compraste por ultima vez cada articulo?"
    ),
    "descripcion_procesos_repetitivos": (
        "Describime la tarea repetitiva que mas tiempo consume hoy."
    ),
    "tiempo_estimado_por_tarea": (
        "Cuantas horas por semana se van en esa tarea?"
    ),
    "herramientas_actuales_usadas": (
        "Que herramientas usas hoy para esa tarea?"
    ),
}


def _evidencia_mas_prioritaria(state: ConversationState) -> tuple[str, str] | None:
    if not state.hipotesis_activas:
        return None

    hipotesis_top = max(state.hipotesis_activas, key=lambda h: h.peso)

    for evidencia in hipotesis_top.evidencia_faltante:
        ya_recibida = evidencia in [d["tipo"] for d in state.datos_conocidos]
        if not ya_recibida:
            return hipotesis_top.codigo, evidencia

    return None


def _pregunta_contexto_prioritaria(state: ConversationState) -> str | None:
    contexto = state.anamnesis_contexto

    orden = ["rubro", "proceso_afectado", "periodo_problema"]
    for campo in orden:
        valor = contexto.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            pregunta = PREGUNTAS_CONTEXTO_CRITICO[campo]
            if not state.pregunta_ya_hecha(pregunta):
                return pregunta

    impacto_economico = contexto.get("impacto_economico_estimado")
    impacto_tiempo = contexto.get("impacto_tiempo")
    if not impacto_economico and not impacto_tiempo:
        pregunta = PREGUNTAS_CONTEXTO_CRITICO["impacto"]
        if not state.pregunta_ya_hecha(pregunta):
            return pregunta

    return None


def next_question(state: ConversationState) -> str:
    """Devuelve la proxima mejor pregunta sin repetir historial."""

    if not state.dolor_principal:
        for pregunta in PREGUNTAS_APERTURA:
            if not state.pregunta_ya_hecha(pregunta):
                return pregunta
        return PREGUNTA_CIERRE

    dimensiones = {
        CATALOGO[h.codigo].dimension
        for h in state.hipotesis_activas
        if h.codigo in CATALOGO
    }

    if state.dimension_foco is None and len(dimensiones) > 1:
        if not state.pregunta_ya_hecha(PREGUNTA_DIMENSION):
            return PREGUNTA_DIMENSION

    pregunta_contexto = _pregunta_contexto_prioritaria(state)
    if pregunta_contexto:
        return pregunta_contexto

    evidencia = _evidencia_mas_prioritaria(state)
    if evidencia:
        _, evidencia_codigo = evidencia
        pregunta = PREGUNTAS_EVIDENCIA.get(
            evidencia_codigo,
            f"Necesito validar esta evidencia: {evidencia_codigo}. La tenes disponible?",
        )

        if not state.pregunta_ya_hecha(pregunta):
            return pregunta

    for hipotesis in sorted(
        state.hipotesis_activas,
        key=lambda hipotesis: hipotesis.peso,
        reverse=True,
    ):
        definicion = CATALOGO.get(hipotesis.codigo)
        if definicion is None:
            continue

        for pregunta in definicion.preguntas_investigacion:
            if not state.pregunta_ya_hecha(pregunta):
                return pregunta

    if not state.pregunta_ya_hecha(PREGUNTA_CIERRE):
        return PREGUNTA_CIERRE

    return (
        "Gracias. Con esto ya tengo suficiente contexto para continuar "
        "la investigacion operacional inicial."
    )


def generar_proxima_pregunta(state: ConversationState) -> str:
    """Alias de compatibilidad con el engine anterior."""

    return next_question(state)
