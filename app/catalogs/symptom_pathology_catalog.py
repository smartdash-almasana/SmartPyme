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
