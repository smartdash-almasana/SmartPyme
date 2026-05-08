"""Generador de próxima pregunta clínica SmartPyme.

Una sola pregunta por turno.
La más informativa posible.
Nunca diagnostica: investiga.
"""

from __future__ import annotations

from app.laboratorio_pyme.conversation.hypotheses import CATALOGO
from app.laboratorio_pyme.conversation.state import ConversationState


PREGUNTAS_APERTURA = [
    "Contame, ¿qué es lo que más te preocupa del negocio ahora mismo?",
    "¿Dónde sentís que el negocio te está fallando hoy?",
    "Si tuvieras que señalar un problema urgente, ¿cuál sería?",
]

PREGUNTA_DIMENSION = (
    "Para enfocarnos mejor: ¿el problema principal hoy es de plata "
    "(margen, caja, costos) o de tiempo (todo manual, tareas repetidas)?"
)

PREGUNTA_CIERRE = (
    "¿Hay algo importante del negocio que todavía no me contaste?"
)


PREGUNTAS_EVIDENCIA: dict[str, str] = {
    "ventas_periodo": (
        "¿Tenés ventas del último trimestre aunque sea en Excel o PDF?"
    ),
    "compras_periodo": (
        "¿Tenés facturas o registros de compras del mismo período?"
    ),
    "lista_precios_vigente": (
        "¿Tenés una lista de precios actual aunque esté desactualizada?"
    ),
    "costo_mercaderia_vendida": (
        "¿Sabés cuánto te costó la mercadería vendida el último mes?"
    ),
    "resumen_caja_diaria": (
        "¿Llevás cierre diario de caja aunque sea manual?"
    ),
    "ventas_registradas": (
        "¿Tenés registro de ventas del último mes?"
    ),
    "egresos_registrados": (
        "¿Registrás pagos, gastos y egresos del negocio?"
    ),
    "inventario_actual": (
        "¿Tenés inventario actualizado del stock actual?"
    ),
    "ultimas_ventas_por_producto": (
        "¿Podés ver qué productos tuvieron movimiento recientemente?"
    ),
    "fecha_ultima_compra_por_item": (
        "¿Sabés cuándo compraste por última vez cada artículo?"
    ),
    "descripcion_procesos_repetitivos": (
        "Describime la tarea repetitiva que más tiempo consume hoy."
    ),
    "tiempo_estimado_por_tarea": (
        "¿Cuántas horas por semana se van en esa tarea?"
    ),
    "herramientas_actuales_usadas": (
        "¿Qué herramientas usás hoy para esa tarea?"
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



def next_question(state: ConversationState) -> str:
    """Devuelve la próxima mejor pregunta sin repetir historial."""

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

    evidencia = _evidencia_mas_prioritaria(state)
    if evidencia:
        _, evidencia_codigo = evidencia
        pregunta = PREGUNTAS_EVIDENCIA.get(
            evidencia_codigo,
            f"Necesito validar esta evidencia: {evidencia_codigo}. ¿La tenés disponible?",
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
        "la investigación operacional inicial."
    )



def generar_proxima_pregunta(state: ConversationState) -> str:
    """Alias de compatibilidad con el engine anterior."""

    return next_question(state)
