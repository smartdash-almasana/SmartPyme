SYMPTOM_CATALOG = {
    "sospecha_perdida_margen": {
        "id": "sospecha_perdida_margen",
        "pathologies": ["erosión_tarifaria", "costo_oculto_insumo"],
        "skills": ["analisis_costeo_margen", "auditoria_tarifas"],
        "variables": ["margen_bruto", "mix_productos", "costo_unitario_real"],
        "evidence": ["reporte_ventas", "listas_precios", "hojas_costos"],
        "questions": ["¿Ha notado un cambio en la composición de ventas?", "¿Se han ajustado los costos de insumos recientemente?"]
    },
    "sospecha_faltante_stock": {
        "id": "sospecha_faltante_stock",
        "pathologies": ["fuga_inventario", "error_ingreso_dato"],
        "skills": ["conciliacion_inventario", "auditoria_procesos_logísticos"],
        "variables": ["stock_teorico", "stock_fisico", "rotacion_inventario"],
        "evidence": ["reporte_inventario", "comprobantes_egreso", "bitacora_movimientos"],
        "questions": ["¿Se realizan conteos físicos periódicos?", "¿Existen ajustes manuales frecuentes en el sistema?"]
    },
    "descuadre_caja_banco": {
        "id": "descuadre_caja_banco",
        "pathologies": ["omision_registro_pago", "doble_contabilizacion"],
        "skills": ["conciliacion_bancaria", "auditoria_financiera"],
        "variables": ["saldo_banco_extracto", "saldo_contable", "transacciones_pendientes"],
        "evidence": ["extracto_bancario", "libro_diario", "conciliaciones_anteriores"],
        "questions": ["¿Se registran las transacciones diariamente?", "¿Hay transacciones sin comprobante asociado?"]
    },
    "exceso_trabajo_manual": {
        "id": "exceso_trabajo_manual",
        "pathologies": ["ineficiencia_operativa", "ausencia_automatizacion"],
        "skills": ["mapeo_procesos", "automatizacion_flujos"],
        "variables": ["horas_hombre_tarea", "tasa_error_manual", "volumen_transacciones"],
        "evidence": ["matriz_tiempos", "reporte_errores", "diagrama_proceso"],
        "questions": ["¿Qué tareas consumen más tiempo de su equipo?", "¿Se utilizan hojas de cálculo para procesos repetitivos?"]
    },
    "incertidumbre_costo_produccion": {
        "id": "incertidumbre_costo_produccion",
        "pathologies": ["ausencia_costeo_estandar", "distorsion_gastos_indirectos"],
        "skills": ["diseño_sistema_costos", "analisis_absorcion_costos"],
        "variables": ["costos_fijos", "costos_variables", "factor_eficiencia"],
        "evidence": ["reporte_produccion", "facturas_servicios", "nomina"],
        "questions": ["¿Cómo se asignan los costos indirectos a los productos?", "¿Se conoce el margen de contribución por producto?"]
    }
}

def get_symptom(symptom_id):
    return SYMPTOM_CATALOG.get(symptom_id)

def get_candidate_pathologies(symptom_id):
    symptom = get_symptom(symptom_id)
    return symptom["pathologies"] if symptom else []

def get_candidate_skills(symptom_id):
    symptom = get_symptom(symptom_id)
    return symptom["skills"] if symptom else []

def get_required_variables(symptom_id):
    symptom = get_symptom(symptom_id)
    return symptom["variables"] if symptom else []

def get_required_evidence(symptom_id):
    symptom = get_symptom(symptom_id)
    return symptom["evidence"] if symptom else []

def get_mayeutic_questions(symptom_id):
    symptom = get_symptom(symptom_id)
    return symptom["questions"] if symptom else []
