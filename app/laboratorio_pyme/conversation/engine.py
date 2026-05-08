from __future__ import annotations

import re

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

MAPA_EVIDENCIA_POR_KEYWORD = {
    "ventas": "ventas_periodo",
    "facturas": "compras_periodo",
    "inventario": "inventario_actual",
    "stock": "inventario_actual",
    "precios": "lista_precios_actual",
    "caja": "resumen_caja_diaria",
    "excel": "herramientas_actuales_usadas",
}

RUBROS_POR_KEYWORD = {
    "kiosco": "kiosco",
    "almacen": "almacen",
    "restaurante": "gastronomia",
    "bar": "gastronomia",
    "panaderia": "panaderia",
    "ferreteria": "ferreteria",
    "farmacia": "farmacia",
    "indumentaria": "indumentaria",
    "ropa": "indumentaria",
    "taller": "taller",
    "ecommerce": "ecommerce",
}

TAMANO_POR_KEYWORD = {
    "solo yo": "micro",
    "yo solo": "micro",
    "somos 2": "micro",
    "somos 3": "micro",
    "somos 4": "pequena",
    "somos 5": "pequena",
    "somos 10": "pequena",
    "equipo de": "reportado_en_texto",
}

URGENCIA_POR_KEYWORD = {
    "hoy": "alta",
    "urgente": "alta",
    "ya": "alta",
    "esta semana": "alta",
    "este mes": "media",
    "puede esperar": "baja",
}

PROCESO_POR_KEYWORD = {
    "caja": "tesoreria_caja",
    "stock": "inventario",
    "inventario": "inventario",
    "precios": "precios",
    "compras": "compras",
    "ventas": "ventas",
    "facturacion": "facturacion",
    "cobranza": "cobranza",
    "excel": "administracion_manual",
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

    for keyword, evidencia in MAPA_EVIDENCIA_POR_KEYWORD.items():
        if keyword in texto:
            state.marcar_evidencia_recibida(evidencia)


def _extraer_contexto_anamnesis(
    mensaje: str,
) -> dict[str, str | list[str] | None]:
    texto = mensaje.lower()
    extraido: dict[str, str | list[str] | None] = {
        "rubro": None,
        "tamano_aprox": None,
        "urgencia": None,
        "impacto_economico_estimado": None,
        "impacto_tiempo": None,
        "proceso_afectado": None,
        "periodo_problema": None,
        "evidencia_disponible": [],
    }

    for keyword, rubro in RUBROS_POR_KEYWORD.items():
        if keyword in texto:
            extraido["rubro"] = rubro
            break

    for keyword, tamano in TAMANO_POR_KEYWORD.items():
        if keyword in texto:
            extraido["tamano_aprox"] = tamano
            break

    for keyword, urgencia in URGENCIA_POR_KEYWORD.items():
        if keyword in texto:
            extraido["urgencia"] = urgencia
            break

    for keyword, proceso in PROCESO_POR_KEYWORD.items():
        if keyword in texto:
            extraido["proceso_afectado"] = proceso
            break

    periodo_match = re.search(
        r"(hace\s+\d+\s+(?:dias|semanas|meses|anos)|"
        r"ultimo\s+mes|ultimos?\s+\d+\s+meses|"
        r"ultimo\s+trimestre|ultimos?\s+\d+\s+dias|"
        r"desde\s+hace\s+\d+\s+(?:dias|semanas|meses|anos))",
        texto,
    )
    if periodo_match:
        extraido["periodo_problema"] = periodo_match.group(0)

    impacto_economico_match = re.search(
        r"(pierdo|perdemos|falta|faltan|cae|bajo|menos)\s+\$?\s*"
        r"([\d\.,]+(?:\s*(?:k|mil|m|millones?))?)",
        texto,
    )
    if impacto_economico_match:
        extraido["impacto_economico_estimado"] = impacto_economico_match.group(2).strip()

    impacto_tiempo_match = re.search(r"(\d+\s*(?:horas?|hs))", texto)
    if impacto_tiempo_match:
        extraido["impacto_tiempo"] = impacto_tiempo_match.group(1).strip()
    elif any(token in texto for token in ("mucho tiempo", "todo manual", "desbordado")):
        extraido["impacto_tiempo"] = "alto_no_cuantificado"

    evidencia_disponible: list[str] = []
    for keyword, evidencia in MAPA_EVIDENCIA_POR_KEYWORD.items():
        if keyword in texto:
            evidencia_disponible.append(evidencia)
    extraido["evidencia_disponible"] = sorted(set(evidencia_disponible))

    return extraido


def _actualizar_contexto_anamnesis(
    state: ConversationState,
    extraido: dict[str, str | list[str] | None],
) -> None:
    contexto = state.anamnesis_contexto

    for key in (
        "rubro",
        "tamano_aprox",
        "urgencia",
        "impacto_economico_estimado",
        "impacto_tiempo",
        "proceso_afectado",
        "periodo_problema",
    ):
        nuevo_valor = extraido.get(key)
        if isinstance(nuevo_valor, str) and nuevo_valor.strip():
            contexto[key] = nuevo_valor.strip()

    evidencia_actual = contexto.get("evidencia_disponible")
    evidencia_lista = list(evidencia_actual) if isinstance(evidencia_actual, list) else []
    nueva_evidencia = extraido.get("evidencia_disponible")
    if isinstance(nueva_evidencia, list):
        for item in nueva_evidencia:
            if isinstance(item, str) and item not in evidencia_lista:
                evidencia_lista.append(item)
    contexto["evidencia_disponible"] = evidencia_lista


def _actualizar_incertidumbres_clinicas(state: ConversationState) -> None:
    contexto = state.anamnesis_contexto
    incertidumbres: list[str] = []

    if not contexto.get("rubro"):
        incertidumbres.append("falta_rubro")
    if not contexto.get("proceso_afectado"):
        incertidumbres.append("falta_proceso_afectado")
    if not contexto.get("periodo_problema"):
        incertidumbres.append("falta_periodo_problema")
    if not contexto.get("impacto_economico_estimado") and not contexto.get("impacto_tiempo"):
        incertidumbres.append("falta_impacto")

    state.incertidumbres = incertidumbres


def procesar_mensaje(state: ConversationState, mensaje: str) -> dict:
    """Procesa un mensaje sin emitir diagnostico definitivo."""

    state.registrar_mensaje(mensaje)

    contexto_extraido = _extraer_contexto_anamnesis(mensaje)
    _actualizar_contexto_anamnesis(state, contexto_extraido)
    _actualizar_incertidumbres_clinicas(state)

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
