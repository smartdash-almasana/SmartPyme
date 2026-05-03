SYMPTOM_CATALOG = {
    "sospecha_perdida_margen": {
        "symptom_id": "sospecha_perdida_margen",
        "name": "Sospecha de pérdida de margen",
        "owner_pains": ["pierdo plata", "vendo pero no gano"],
        "operational_symptom": "Deterioro del margen real frente al esperado",
        "candidate_pathologies": ["desalineacion_costo_precio", "costo_reposicion_desactualizado"],
        "hypothesis_template": "Investigar si existe pérdida de margen por desalineación de costos en {periodo}.",
        "candidate_skills": ["skill_margin_leak_audit"],
        "required_variables": ["periodo", "margen_esperado"],
        "required_evidence": ["ventas_pos", "facturas_proveedor"],
        "required_knowledge": ["doctrina_costeo_margen", "teoria_precios"],
        "source_candidates": ["tanque_contable_sectorial"],
        "research_questions": ["¿Cómo afecta la inflación al costo de reposición?"],
        "mayeutic_questions": ["¿Qué período querés revisar?"],
        "advance_criteria": ["existe_periodo", "existe_evidencia"],
        "blocking_criteria": ["no_hay_periodo"]
    },
    "sospecha_faltante_stock": {
        "symptom_id": "sospecha_faltante_stock",
        "name": "Sospecha de faltante de stock",
        "owner_pains": ["me desaparecen productos", "no coinciden cantidades"],
        "operational_symptom": "Diferencia entre stock teórico y físico",
        "candidate_pathologies": ["merma", "robo_hormiga"],
        "hypothesis_template": "Investigar diferencias de stock en {periodo}.",
        "candidate_skills": ["skill_stock_loss_detect"],
        "required_variables": ["periodo", "stock_fisico"],
        "required_evidence": ["inventario_fisico", "reporte_movimientos"],
        "required_knowledge": ["control_inventario", "gestion_deposito"],
        "source_candidates": ["tanque_logistico"],
        "research_questions": ["¿Qué procesos generan más mermas?"],
        "mayeutic_questions": ["¿Tenés inventario físico reciente?"],
        "advance_criteria": ["existe_inventario"],
        "blocking_criteria": ["no_hay_inventario"]
    },
    "descuadre_caja_banco": {
        "symptom_id": "descuadre_caja_banco",
        "name": "Descuadre caja y banco",
        "owner_pains": ["no me cierra la caja", "no me cierra el banco"],
        "operational_symptom": "Diferencia en conciliación financiera",
        "candidate_pathologies": ["conciliacion_fallida", "ventas_no_registradas"],
        "hypothesis_template": "Investigar descuadre en conciliación durante {periodo}.",
        "candidate_skills": ["skill_reconcile_bank_vs_pos"],
        "required_variables": ["periodo", "saldo_banco"],
        "required_evidence": ["extracto_bancario", "libro_diario"],
        "required_knowledge": ["conciliacion_bancaria", "flujo_caja"],
        "source_candidates": ["tanque_financiero"],
        "research_questions": ["¿Qué métodos de pago son más frecuentes?"],
        "mayeutic_questions": ["¿Tenés extractos bancarios?"]
    },
    "exceso_trabajo_manual": {
        "symptom_id": "exceso_trabajo_manual",
        "name": "Exceso de trabajo manual",
        "owner_pains": ["trabajo demasiado manual", "muchas planillas"],
        "operational_symptom": "Ineficiencia operativa por tareas repetitivas",
        "candidate_pathologies": ["falta_automatizacion", "procesos_desintegrados"],
        "hypothesis_template": "Investigar ineficiencia en procesos de {proceso}.",
        "candidate_skills": ["skill_process_automation_audit"],
        "required_variables": ["horas_hombre", "tasa_error"],
        "required_evidence": ["diagrama_proceso", "bitacora_tareas"],
        "required_knowledge": ["mapeo_procesos", "automatizacion"],
        "source_candidates": ["tanque_operaciones"],
        "research_questions": ["¿Qué tareas consumen más tiempo?"],
        "mayeutic_questions": ["¿Tenés un mapa de tus procesos?"]
    },
    "incertidumbre_costo_produccion": {
        "symptom_id": "incertidumbre_costo_produccion",
        "name": "Incertidumbre costo producción",
        "owner_pains": ["no sé si me conviene producir"],
        "operational_symptom": "Distorción en costo de producto final",
        "candidate_pathologies": ["BOM_incompleto", "costos_indirectos_mal_asignados"],
        "hypothesis_template": "Investigar estructura de costos para {producto}.",
        "candidate_skills": ["skill_bom_cost_audit"],
        "required_variables": ["producto", "costos_indirectos"],
        "required_evidence": ["facturas_insumos", "nomina"],
        "required_knowledge": ["costeo_absorcion", "ingenieria_costos"],
        "source_candidates": ["tanque_produccion"],
        "research_questions": ["¿Cómo asignás los indirectos?"],
        "mayeutic_questions": ["¿Tenés la receta de producción?"]
    }
}

def get_symptom(sid): return SYMPTOM_CATALOG.get(sid)
def list_symptoms(): return list(SYMPTOM_CATALOG.keys())
def get_candidate_pathologies(sid): return get_symptom(sid).get("candidate_pathologies", [])
def get_candidate_skills(sid): return get_symptom(sid).get("candidate_skills", [])
def get_required_variables(sid): return get_symptom(sid).get("required_variables", [])
def get_required_evidence(sid): return get_symptom(sid).get("required_evidence", [])
def get_required_knowledge(sid): return get_symptom(sid).get("required_knowledge", [])
def get_source_candidates(sid): return get_symptom(sid).get("source_candidates", [])
def get_research_questions(sid): return get_symptom(sid).get("research_questions", [])
def get_mayeutic_questions(sid): return get_symptom(sid).get("mayeutic_questions", [])
