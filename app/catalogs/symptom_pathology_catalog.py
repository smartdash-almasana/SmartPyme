SYMPTOM_CATALOG = {
    "sospecha_perdida_margen": {
        "symptom_id": "sospecha_perdida_margen",
        "name": "Sospecha de pérdida de margen",
        "owner_pains": ["pierdo plata", "vendo pero no gano"],
        "operational_symptom": "Deterioro del margen real frente al esperado",
        "candidate_pathologies": ["desalineacion_costo_precio", "costo_reposicion_desactualizado"],
        "hypothesis_template": "Investigar si existe pérdida de margen por desalineación de costos en {periodo}.",
        "candidate_skills": ["skill_margin_leak_audit"],
        "required_variables": ["periodo", "margen_esperado", "productos_o_familias"],
        "required_evidence": ["ventas_pos", "facturas_proveedor"],
        "required_knowledge": ["doctrina_costeo_margen", "teoria_precios"],
        "source_candidates": ["tanque_contable_sectorial"],
        "research_questions": ["¿Cómo afecta la inflación al costo de reposición?"],
        "mayeutic_questions": ["¿Qué período querés revisar?", "¿Qué productos o familias querés analizar?"],
        "advance_criteria": ["existe_periodo", "existe_evidencia"],
        "blocking_criteria": ["no_hay_periodo"],
    },

    "sospecha_faltante_stock": {
        "symptom_id": "sospecha_faltante_stock",
        "name": "Sospecha de faltante de stock",
        "owner_pains": ["me quedo sin mercadería", "pierdo ventas por falta de stock", "siempre me falta algo"],
        "operational_symptom": "Ruptura de stock recurrente en productos de alta rotación",
        "candidate_pathologies": ["punto_reposicion_desactualizado", "demanda_subestimada"],
        "hypothesis_template": "Investigar si existe faltante de stock sistemático en {periodo} para {producto}.",
        "candidate_skills": ["skill_stock_loss_detect"],
        "required_variables": ["periodo", "producto", "stock_minimo_esperado"],
        "required_evidence": ["movimientos_stock", "ordenes_compra"],
        "required_knowledge": ["control_inventario", "teoria_punto_reposicion"],
        "source_candidates": ["sistema_stock_interno", "historial_compras"],
        "research_questions": [
            "¿Cuál es la frecuencia de ruptura de stock en los últimos 3 meses?",
            "¿Existe un punto de reposición definido para los productos críticos?",
        ],
        "mayeutic_questions": [
            "¿Qué productos se quedan sin stock con más frecuencia?",
            "¿Cuántos días tarda en llegar la mercadería una vez pedida?",
        ],
        "advance_criteria": ["existe_historial_movimientos", "existe_producto_critico"],
        "blocking_criteria": ["no_hay_historial_stock"],
    },

    "caida_ventas_recurrentes": {
        "symptom_id": "caida_ventas_recurrentes",
        "name": "Caída de ventas recurrente",
        "owner_pains": ["vendo menos cada mes", "los clientes no vuelven", "bajaron las ventas"],
        "operational_symptom": "Tendencia descendente sostenida en volumen o valor de ventas",
        "candidate_pathologies": ["perdida_clientes_activos", "mix_ventas_deteriorado"],
        "hypothesis_template": "Investigar si existe caída sostenida de ventas en {periodo} por {causa_probable}.",
        "candidate_skills": ["skill_reconcile_bank_vs_pos"],
        "required_variables": ["periodo", "canal_venta", "segmento_cliente"],
        "required_evidence": ["historial_ventas", "base_clientes"],
        "required_knowledge": ["analisis_tendencias_ventas", "segmentacion_clientes"],
        "source_candidates": ["sistema_facturacion", "pos_ventas"],
        "research_questions": [
            "¿La caída es en todos los productos o en algunos específicos?",
            "¿Se perdieron clientes recurrentes o bajó el ticket promedio?",
        ],
        "mayeutic_questions": [
            "¿Desde cuándo notás que bajan las ventas?",
            "¿Hay algún producto o canal donde la caída sea más notoria?",
        ],
        "advance_criteria": ["existe_historial_ventas", "existe_periodo_comparacion"],
        "blocking_criteria": ["no_hay_historial_ventas"],
    },

    "exceso_stock_inmovilizado": {
        "symptom_id": "exceso_stock_inmovilizado",
        "name": "Exceso de stock inmovilizado",
        "owner_pains": ["tengo plata parada en mercadería", "no rota el stock", "lleno de cosas que no vendo"],
        "operational_symptom": "Acumulación de inventario con baja rotación que inmoviliza capital",
        "candidate_pathologies": ["sobrecompra_sistematica", "productos_obsoletos_sin_liquidar"],
        "hypothesis_template": "Investigar si existe stock inmovilizado en {periodo} que supera {umbral_dias} días de rotación.",
        "candidate_skills": ["skill_bom_cost_audit"],
        "required_variables": ["periodo", "umbral_dias_rotacion", "categoria_producto"],
        "required_evidence": ["inventario_actual", "historial_ventas"],
        "required_knowledge": ["rotacion_inventario", "costo_capital_inmovilizado"],
        "source_candidates": ["sistema_stock_interno", "sistema_facturacion"],
        "research_questions": [
            "¿Cuántos días promedio tarda en venderse cada categoría de producto?",
            "¿Hay productos que no se vendieron en los últimos 90 días?",
        ],
        "mayeutic_questions": [
            "¿Qué categorías de productos sentís que no rotan?",
            "¿Cuánto capital estimás que tenés parado en mercadería sin movimiento?",
        ],
        "advance_criteria": ["existe_inventario_actual", "existe_historial_ventas"],
        "blocking_criteria": ["no_hay_inventario_valorizado"],
    },

    "desorden_cobranzas_clientes": {
        "symptom_id": "desorden_cobranzas_clientes",
        "name": "Desorden en cobranzas a clientes",
        "owner_pains": ["me deben y no cobro", "los clientes pagan cuando quieren", "tengo cuentas a cobrar vencidas"],
        "operational_symptom": "Cuentas a cobrar vencidas con alta antigüedad y sin seguimiento sistemático",
        "candidate_pathologies": ["politica_credito_laxa", "proceso_cobranza_inexistente"],
        "hypothesis_template": "Investigar si existe desorden en cobranzas en {periodo} con saldos vencidos superiores a {umbral_dias} días.",
        "candidate_skills": ["skill_process_automation_audit"],
        "required_variables": ["periodo", "umbral_dias_vencimiento", "segmento_cliente"],
        "required_evidence": ["cuentas_a_cobrar", "historial_pagos_clientes"],
        "required_knowledge": ["gestion_credito_cobranza", "flujo_caja_operativo"],
        "source_candidates": ["sistema_contable", "crm_clientes"],
        "research_questions": [
            "¿Cuál es el plazo promedio real de cobro versus el plazo acordado?",
            "¿Qué porcentaje de las cuentas a cobrar tiene más de 60 días de antigüedad?",
        ],
        "mayeutic_questions": [
            "¿Cuántos clientes te deben plata hoy?",
            "¿Tenés definido un proceso de seguimiento de cobranzas?",
        ],
        "advance_criteria": ["existe_cuentas_cobrar", "existe_historial_pagos"],
        "blocking_criteria": ["no_hay_registro_deudores"],
    },
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
