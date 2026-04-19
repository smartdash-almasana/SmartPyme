from typing import List, Dict, Any
from app.modules.findings_engine import procesar_extraccion_bruta
from pydantic import ValidationError

def ejecutar_pipeline_extraccion(datos_entrada: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Punto de entrada mínimo al pipeline orquestador en SmartPyme.
    Recibe la extracción simulada en bruto, direcciona los hallazgos al engine puro
    y formatea el estado final determinístico impidiendo caídas letales silenciosas.
    
    Contrato de salida de wrapper:
    - status: 'success' | 'error'
    - hallazgos_procesados: List[Dict] serializados sin fallos.
    - errores: List[str] describiendo roturas en validación.
    """
    estado_pipeline = {
        "status": "success",
        "hallazgos_procesados": [],
        "errores": []
    }
    
    if not isinstance(datos_entrada, list):
        estado_pipeline["status"] = "error"
        estado_pipeline["errores"].append("El payload de entrada debe ser obligatoriamente una lista de diccionarios.")
        return estado_pipeline

    try:
        hallazgos_validos = procesar_extraccion_bruta(datos_entrada)
        estado_pipeline["hallazgos_procesados"] = hallazgos_validos
    except ValidationError as e:
        # Pydantic arrojará esto cuando faltan keys o violas el Schema básico
        # Debe ir primero porque ValidationError hereda de ValueError
        estado_pipeline["status"] = "error"
        estado_pipeline["errores"].append(f"Payload incompleto o con formato inválido: {str(e)}")
    except ValueError as e:
        # Esto atrapará nuestra restricción principal (e.g. floats insertados en strings)
        estado_pipeline["status"] = "error"
        estado_pipeline["errores"].append(f"Error de valor crítico: {str(e)}")
    except Exception as e:
        estado_pipeline["status"] = "error"
        estado_pipeline["errores"].append(f"Error sistémico insondable: {str(e)}")

    return estado_pipeline
