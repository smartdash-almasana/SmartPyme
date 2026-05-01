"""
Catálogo Determinístico de Patologías (SmartCounter Core).
Toda patología operativa debe estar registrada aquí de forma auditable.
No se permite inyección dinámica de patologías omitidas aquí.
"""

CATALOGO_PATOLOGIAS = {
    "IVA_DESGLOSE_ERROR": {
        "patologia_id": "IVA_DESGLOSE_ERROR",
        "nombre": "Error en desglose de tributos (IVA)",
        "descripcion_corta": (
            "El monto o alícuota de IVA reportado difiere de la "
            "expectativa oficial."
        ),
        "nivel_severidad_default": "alto",
    },
    "FORMATO_CSV_CAOTICO_AR": {
        "patologia_id": "FORMATO_CSV_CAOTICO_AR",
        "nombre": "CSV AFIP o reporte caótico",
        "descripcion_corta": (
            "Formato de reporte dañado, delimitadores o columnas inconsistentes."
        ),
        "nivel_severidad_default": "medio",
    },
}
