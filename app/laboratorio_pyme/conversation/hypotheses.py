from __future__ import annotations

HIPOTESIS = {
    "margen_erosionado": {
        "keywords": ["vendo mucho", "no queda plata", "margen", "costos"],
        "evidencia": ["ventas_periodo", "compras_periodo", "lista_precios"],
        "pregunta": "Para verificar margen real necesito ventas y compras del mismo período. ¿Tenés esas planillas?",
    },
    "stock_inmovilizado": {
        "keywords": ["stock", "parado", "mercadería", "inmovilizado"],
        "evidencia": ["stock_actual", "ventas_por_producto"],
        "pregunta": "¿Tenés una planilla de stock actual y otra de ventas por producto para revisar rotación?",
    },
    "caja_inconsistente": {
        "keywords": ["caja", "plata", "flujo", "no alcanza"],
        "evidencia": ["caja_diaria", "ventas_cobradas"],
        "pregunta": "Necesito validar flujo de caja. ¿Tenés caja diaria o movimientos cobrados del período?",
    },
    "precios_atrasados": {
        "keywords": ["precios", "inflación", "reposicion", "aumentos"],
        "evidencia": ["listas_historicas", "costos_reposicion"],
        "pregunta": "¿Tenés listas históricas de precios y costos para comparar reposición?",
    },
    "tiempo_perdido": {
        "keywords": ["tiempo", "repetitivas", "demora", "manual"],
        "evidencia": ["procesos_operativos", "tareas_repetitivas"],
        "pregunta": "¿Qué tareas sentís que más tiempo consumen todos los días?",
    },
}
