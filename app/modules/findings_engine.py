from typing import Any

from app.catalog.patologias import CATALOGO_PATOLOGIAS
from app.core.calculators import calcular_diferencia_absoluta
from app.core.entities import HallazgoOperativo


def procesar_extraccion_bruta(datos_crudos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Engine mínimo para evaluar datos crudos y emitir hallazgos validados.
    Aplica el contrato determinístico bloqueando floats o datos corruptos
    antes de serializar la salida hacia la capa de orquestación.
    Constriñe dinámicamente las patologías contra el catálogo principal.
    Aplica determinismo matemático local a la trazabilidad de "diferencia".
    """
    hallazgos_exportados = []
    
    for payload in datos_crudos:
        pid = payload.get("patologia_id")
        if not pid or not isinstance(pid, str):
            raise ValueError("El campo patologia_id es inexistente o estructuralmente inválido.")
            
        pid = pid.strip()
        if pid not in CATALOGO_PATOLOGIAS:
            raise ValueError(f"Patología no reconocida por el sistema auditado: {pid}")

        # Integración Determinística de Diferencia
        # Si la ráfaga de datos crudos aporta los contrapesos
        # (monto detectado y monto de contraste o esperado),
        # anula/asigna la diferencia matemáticamente de modo local,
        # rechazando pre-cálculos de la capa integradora si fuera el caso.
        if "monto_detectado" in payload and "monto_esperado" in payload:
            diferencia_rigor = calcular_diferencia_absoluta(
                payload["monto_detectado"],
                payload["monto_esperado"],
            )
            payload["diferencia"] = diferencia_rigor
            
        # Inyectamos el nivel de severidad por asunción determinística si no se provee nada
        if "nivel_severidad" not in payload or not str(payload["nivel_severidad"]).strip():
            payload["nivel_severidad"] = CATALOGO_PATOLOGIAS[pid]["nivel_severidad_default"]

        hallazgo_obj = HallazgoOperativo(**payload)
        hallazgos_exportados.append(hallazgo_obj.model_dump(mode='json'))
        
    return hallazgos_exportados
