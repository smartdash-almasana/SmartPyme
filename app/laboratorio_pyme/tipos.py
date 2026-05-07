from __future__ import annotations
from enum import Enum


class TipoLaboratorio(str, Enum):
    """Laboratorios disponibles en el MVP del Laboratorio de Análisis PyME."""

    analisis_comercial = "analisis_comercial"
    analisis_stock = "analisis_stock"
    analisis_financiero = "analisis_financiero"
    analisis_compras = "analisis_compras"
    analisis_automatizacion = "analisis_automatizacion"
