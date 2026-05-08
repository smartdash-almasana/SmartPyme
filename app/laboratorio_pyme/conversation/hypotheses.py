"""Catálogo clínico de hipótesis SmartPyme.

Cada hipótesis es una posibilidad investigativa, nunca un diagnóstico.
Estructura:
    síntomas -> hipótesis -> evidencia -> preguntas.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DefinicionHipotesis:
    codigo: str
    nombre: str
    descripcion: str
    dimension: str
    sintomas: list[str]
    evidencia_requerida: list[str]
    preguntas_investigacion: list[str]
    peso_inicial: float = 0.4
    subsistemas_afectados: list[str] | None = None


CATALOGO: dict[str, DefinicionHipotesis] = {
    "margen_erosionado": DefinicionHipotesis(
        codigo="margen_erosionado",
        nombre="Margen Erosionado",
        descripcion=(
            "Las ventas se sostienen pero la rentabilidad cae por costos, inflación o precios atrasados."
        ),
        dimension="dinero",
        sintomas=[
            "vendo mucho pero no queda plata",
            "no queda nada",
            "vendo y no gano",
            "los costos subieron",
            "aumentaron los costos",
            "no me cierra",
            "trabajo para los proveedores",
            "el margen bajo",
            "menos ganancia",
            "vendo más y gano menos",
        ],
        evidencia_requerida=[
            "ventas_periodo",
            "compras_periodo",
            "lista_precios_vigente",
            "costo_mercaderia_vendida",
        ],
        preguntas_investigacion=[
            "¿Tenés registros de ventas del último trimestre aunque sea en Excel?",
            "¿Actualizaste precios cuando subieron los costos?",
            "¿Cuándo fue la última vez que calculaste margen por producto?",
        ],
        peso_inicial=0.5,
        subsistemas_afectados=["ventas", "precios", "rentabilidad"],
    ),
    "caja_inconsistente": DefinicionHipotesis(
        codigo="caja_inconsistente",
        nombre="Caja Inconsistente",
        descripcion=(
            "El dinero disponible no coincide con las ventas o movimientos esperados."
        ),
        dimension="dinero",
        sintomas=[
            "la plata no cierra",
            "falta dinero en caja",
            "la caja no bate",
            "no sé a dónde fue la plata",
            "faltan billetes",
            "vendí pero no tengo la plata",
            "siempre me falta",
            "no me cuadra",
            "los números no cierran",
        ],
        evidencia_requerida=[
            "resumen_caja_diaria",
            "ventas_registradas",
            "egresos_registrados",
        ],
        preguntas_investigacion=[
            "¿Llevás algún cierre de caja diario?",
            "¿Los gastos personales y del negocio están mezclados?",
            "¿Más de una persona maneja la caja?",
        ],
        peso_inicial=0.45,
        subsistemas_afectados=["caja", "tesoreria"],
    ),
    "stock_inmovilizado": DefinicionHipotesis(
        codigo="stock_inmovilizado",
        nombre="Stock Inmovilizado",
        descripcion=(
            "Capital atrapado en mercadería con baja rotación o sin salida."
        ),
        dimension="dinero",
        sintomas=[
            "tengo mucho stock parado",
            "mercadería que no sale",
            "el depósito está lleno",
            "compré de más",
            "stock que no rota",
            "productos sin movimiento",
        ],
        evidencia_requerida=[
            "inventario_actual",
            "ultimas_ventas_por_producto",
            "fecha_ultima_compra_por_item",
        ],
        preguntas_investigacion=[
            "¿Tenés un inventario actualizado aunque sea básico?",
            "¿Qué productos no tuvieron movimiento recientemente?",
            "¿Comprás por volumen aunque no lo necesites todavía?",
        ],
        peso_inicial=0.5,
        subsistemas_afectados=["stock", "compras", "deposito"],
    ),
    "precios_atrasados": DefinicionHipotesis(
        codigo="precios_atrasados",
        nombre="Precios Atrasados",
        descripcion=(
            "Los precios de venta quedaron detrás de los costos de reposición."
        ),
        dimension="dinero",
        sintomas=[
            "no actualicé los precios",
            "los precios están viejos",
            "me da vergüenza subir los precios",
            "no sé cómo poner precio",
            "el cliente se queja si subo",
            "hace meses que no retoco la lista",
            "los precios están desactualizados",
        ],
        evidencia_requerida=[
            "lista_precios_actual",
            "fecha_ultima_actualizacion_precios",
            "facturas_proveedores_recientes",
        ],
        preguntas_investigacion=[
            "¿Cuándo actualizaste precios por última vez?",
            "¿Calculás precios usando costos actuales?",
            "¿Tenés una lista de precios formal?",
        ],
        peso_inicial=0.4,
        subsistemas_afectados=["precios", "reposicion"],
    ),
    "tiempo_perdido": DefinicionHipotesis(
        codigo="tiempo_perdido",
        nombre="Tiempo Perdido en Tareas Repetitivas",
        descripcion=(
            "El dueño o equipo pierde horas en procesos manuales repetitivos."
        ),
        dimension="tiempo",
        sintomas=[
            "pierdo mucho tiempo en tareas repetidas",
            "hago lo mismo todos los días",
            "cargo datos a mano",
            "paso horas en el Excel",
            "copiopegoteo entre planillas",
            "todo es manual",
            "no me alcanza el tiempo",
            "estoy desbordado",
        ],
        evidencia_requerida=[
            "descripcion_procesos_repetitivos",
            "tiempo_estimado_por_tarea",
            "herramientas_actuales_usadas",
        ],
        preguntas_investigacion=[
            "¿Qué tarea repetitiva consume más tiempo?",
            "¿Cuántas horas por semana se van ahí?",
            "¿Usás Excel, sistema o papel para esa tarea?",
        ],
        peso_inicial=0.5,
        subsistemas_afectados=["operaciones", "administracion"],
    ),
}


HIPOTESIS = {
    codigo: {
        "keywords": definicion.sintomas,
        "evidencia": definicion.evidencia_requerida,
        "pregunta": definicion.preguntas_investigacion[0],
    }
    for codigo, definicion in CATALOGO.items()
}


def buscar_hipotesis_por_sintoma(mensaje: str) -> list[tuple[str, float]]:
    """Devuelve hipótesis activadas con peso incremental."""

    mensaje_lower = mensaje.lower()
    activadas: list[tuple[str, float]] = []

    for codigo, hipotesis in CATALOGO.items():
        coincidencias = sum(
            1
            for sintoma in hipotesis.sintomas
            if sintoma in mensaje_lower
        )

        if coincidencias > 0:
            peso = min(
                hipotesis.peso_inicial + ((coincidencias - 1) * 0.1),
                0.85,
            )
            activadas.append((codigo, peso))

    activadas.sort(key=lambda item: item[1], reverse=True)
    return activadas
