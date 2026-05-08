from __future__ import annotations

from app.laboratorio_pyme.conversation.hypotheses import (
    CATALOGO,
    buscar_hipotesis_por_sintoma,
)
from app.laboratorio_pyme.conversation.questions import generar_proxima_pregunta
from app.laboratorio_pyme.conversation.state import ConversationState


DIMENSIONES_DINERO = {
    "margen",
    "plata",
    "caja",
    "costos",
    "ventas",
    "precios",
    "rentabilidad",
    "stock",
}

DIMENSIONES_TIEMPO = {
    "tiempo",
    "manual",
    "repetitivas",
    "repetidas",
    "excel",
    "horas",
    "desbordado",
    "procesos",
}



def _detectar_dimension(mensaje: str) -> str | None:
    texto = mensaje.lower()

    dinero = any(token in texto for token in DIMENSIONES_DINERO)
    tiempo = any(token in texto for token in DIMENSIONES_TIEMPO)

    if dinero and tiempo:
        return "ambas"
    if dinero:
        return "dinero"
    if tiempo:
        return "tiempo"

    return None



def _actualizar_dimension(state: ConversationState, dimension: str | None) -> None:
    if dimension is None:
        return

    if state.dimension_foco is None:
        state.dimension_foco = dimension
        return

    if state.dimension_foco != dimension:
        state.dimension_foco = "ambas"



def _activar_hipotesis(state: ConversationState, mensaje: str) -> None:
    activadas = buscar_hipotesis_por_sintoma(mensaje)

    for codigo, peso in activadas:
        definicion = CATALOGO[codigo]

        state.activar_o_reforzar_hipotesis(
            codigo=definicion.codigo,
            nombre=definicion.nombre,
            peso=peso,
            dimension=definicion.dimension,
            evidencia_faltante=definicion.evidencia_requerida,
            subsistemas_afectados=definicion.subsistemas_afectados or [],
        )



def _inferir_evidencia_desde_mensaje(
    state: ConversationState,
    mensaje: str,
) -> None:
    texto = mensaje.lower()

    mapa_evidencia = {
        "ventas": "ventas_periodo",
        "facturas": "compras_periodo",
        "inventario": "inventario_actual",
        "stock": "inventario_actual",
        "precios": "lista_precios_actual",
        "caja": "resumen_caja_diaria",
        "excel": "herramientas_actuales_usadas",
    }

    for keyword, evidencia in mapa_evidencia.items():
        if keyword in texto:
            state.marcar_evidencia_recibida(evidencia)



def procesar_mensaje(state: ConversationState, mensaje: str) -> dict:
    """Procesa un mensaje sin emitir diagnóstico definitivo."""

    state.registrar_mensaje(mensaje)

    dimension_detectada = _detectar_dimension(mensaje)
    _actualizar_dimension(state, dimension_detectada)

    _activar_hipotesis(state, mensaje)
    _inferir_evidencia_desde_mensaje(state, mensaje)

    state.actualizar_fase()

    pregunta = generar_proxima_pregunta(state)
    state.registrar_pregunta(pregunta)

    return {
        "cliente_id": state.cliente_id,
        "estado": state.estado,
        "fase": state.fase.value,
        "pregunta": pregunta,
        "proxima_pregunta": pregunta,
        "hipotesis_activas": [
            hipotesis.codigo
            for hipotesis in state.hipotesis_activas
        ],
        "evidencia_requerida": state.evidencia_requerida,
        "dimension_detectada": state.dimension_foco,
        "diagnostico_emitido": False,
        "diagnostico_final": None,
        "incertidumbres": state.incertidumbres,
    }
