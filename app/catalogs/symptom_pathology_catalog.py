import dataclasses
from typing import Dict, Optional, Tuple

@dataclasses.dataclass(frozen=True, slots=True)
class SymptomEntry:
    symptom_id: str
    nombre: str
    dolores_asociados: Tuple[str, ...]
    sintoma_operativo: str
    patologias_posibles: Tuple[str, ...]
    hipotesis_template: str
    skills_candidatas: Tuple[str, ...]
    variables_necesarias: Tuple[str, ...]
    evidencia_requerida: Tuple[str, ...]
    preguntas_mayeuticas: Tuple[str, ...]
    criterios_para_avanzar: Tuple[str, ...]
    criterios_de_bloqueo: Tuple[str, ...]

SYMPTOM_PATHOLOGY_CATALOG: Dict[str, SymptomEntry] = {
    "sospecha_perdida_margen": SymptomEntry(
        symptom_id="sospecha_perdida_margen",
        nombre="Sospecha de pérdida de margen",
        dolores_asociados=(
            "pierdo plata",
            "vendo pero no gano",
            "no me deja margen",
            "los proveedores aumentaron",
            "no sé si estoy vendiendo bien",
            "me aumentaron los costos",
            "no sé si los precios están actualizados",
        ),
        sintoma_operativo="Sospecha de deterioro del margen real frente al margen esperado.",
        patologias_posibles=(
            "desalineacion_costo_precio",
            "costo_reposicion_desactualizado",
            "descuentos_no_controlados",
            "mix_productos_deteriorado",
            "comisiones_impuestos_no_imputados",
            "merma_stock_impactando_margen",
        ),
        hipotesis_template="Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante {periodo}.",
        skills_candidatas=("skill_margin_leak_audit",),
        variables_necesarias=(
            "periodo",
            "productos_o_familias",
            "margen_esperado",
            "precio_venta_real",
            "costo_reposicion",
        ),
        evidencia_requerida=(
            "ventas_pos",
            "excel_ventas",
            "facturas_proveedor",
            "lista_costos",
            "promociones_descuentos",
            "inventario_merma_si_aplica",
        ),
        preguntas_mayeuticas=(
            "¿Qué período querés revisar?",
            "¿Querés revisar todos los productos o una familia puntual?",
            "¿Tenés ventas y facturas de proveedor de ese período?",
            "¿Tenés una lista de precios o costos actualizada?",
            "¿Hay promociones o descuentos especiales que apliquen?",
        ),
        criterios_para_avanzar=(
            "existe demanda_original",
            "existe periodo o posibilidad de pedirlo",
            "existe evidencia de ventas o costos",
            "existe skill candidata",
        ),
        criterios_de_bloqueo=(
            "no hay ventas ni costos",
            "no hay período",
            "no hay productos o familias identificables",
        ),
    ),
    "sospecha_faltante_stock": SymptomEntry(
        symptom_id="sospecha_faltante_stock",
        nombre="Sospecha de faltante o pérdida de stock",
        dolores_asociados=(
            "no sé si me falta stock",
            "el inventario no coincide",
            "compro pero no aparece",
            "me desaparecen productos",
            "no me cierran las cantidades",
            "tengo diferencias entre sistema y depósito",
        ),
        sintoma_operativo="Diferencia sospechada entre stock teórico y stock físico.",
        patologias_posibles=(
            "merma",
            "robo_hormiga",
            "ventas_no_registradas",
            "compras_no_asentadas",
            "errores_de_carga",
            "ajustes_de_stock_no_documentados",
        ),
        hipotesis_template="Investigar si existe faltante de stock comparando stock teórico, ventas, compras e inventario físico durante {periodo}.",
        skills_candidatas=("skill_stock_loss_detect",),
        variables_necesarias=(
            "periodo",
            "productos_o_familias",
            "stock_teorico",
            "stock_fisico",
            "ajuste_merma",
        ),
        evidencia_requerida=(
            "inventario_fisico",
            "ventas_pos",
            "compras",
            "ajustes_stock",
            "movimientos_deposito",
        ),
        preguntas_mayeuticas=(
            "¿Querés revisar todos los productos o una familia puntual?",
            "¿Tenés inventario físico reciente?",
            "¿Tenés ventas y compras del período?",
            "¿Hay ajustes manuales de stock?",
            "¿Hay movimientos de depósito registrados?",
        ),
        criterios_para_avanzar=(
            "existe stock físico o stock teórico",
            "existe período",
            "existe evidencia de ventas/compras o inventario",
        ),
        criterios_de_bloqueo=(
            "no hay inventario ni ventas/compras",
            "no hay producto/familia a revisar",
        ),
    ),
    "descuadre_caja_banco": SymptomEntry(
        symptom_id="descuadre_caja_banco",
        nombre="Diferencia entre caja, ventas y banco",
        dolores_asociados=(
            "no me cierra la caja",
            "no me cierra el banco",
            "me falta plata",
            "las ventas no coinciden con los depósitos",
            "no sé dónde está la diferencia",
            "Mercado Pago no me coincide",
        ),
        sintoma_operativo="Diferencia entre ventas registradas, cobros y depósitos bancarios.",
        patologias_posibles=(
            "conciliacion_bancaria_fallida",
            "ventas_no_registradas",
            "comisiones_no_consideradas",
            "retiros_no_documentados",
            "diferencias_por_medios_de_pago",
            "errores_de_cierre_de_caja",
        ),
        hipotesis_template="Investigar si existe descuadre entre ventas registradas, cobros y depósitos bancarios durante {periodo}.",
        skills_candidatas=("skill_reconcile_bank_vs_pos",),
        variables_necesarias=(
            "periodo",
            "pos_total",
            "bank_total",
            "medios_de_pago",
        ),
        evidencia_requerida=(
            "extracto_bancario",
            "reporte_pos",
            "caja_diaria",
            "liquidaciones_mp_tarjetas",
            "comprobantes_retiros",
        ),
        preguntas_mayeuticas=(
            "¿Qué período querés conciliar?",
            "¿Tenés extracto bancario y reporte de ventas?",
            "¿Querés comparar banco contra POS, caja diaria o Mercado Pago?",
            "¿Hay retiros o gastos en efectivo no registrados?",
            "¿Tenés liquidaciones de Mercado Pago o tarjetas?",
        ),
        criterios_para_avanzar=(
            "existe período",
            "existe al menos una fuente de ventas",
            "existe al menos una fuente bancaria/cobro",
        ),
        criterios_de_bloqueo=(
            "no hay extracto ni reporte de ventas",
            "no hay período",
        ),
    ),
    "exceso_trabajo_manual": SymptomEntry(
        symptom_id="exceso_trabajo_manual",
        nombre="Repetición operativa innecesaria",
        dolores_asociados=(
            "trabajo demasiado manual",
            "pasamos muchos Excel a mano",
            "dependo de una persona para cargar todo",
            "se repite el mismo trabajo todas las semanas",
            "perdemos tiempo copiando datos",
            "hay errores por carga manual",
        ),
        sintoma_operativo="Flujo operativo repetitivo, manual y propenso a errores.",
        patologias_posibles=(
            "falta_automatizacion",
            "duplicacion_de_carga",
            "dependencia_de_personas",
            "ausencia_de_integracion",
            "riesgo_error_humano",
            "perdida_tiempo_operativo",
        ),
        hipotesis_template="Investigar si existe pérdida de tiempo y riesgo operativo por repetición manual de tareas en el flujo {flujo_operativo}.",
        skills_candidatas=("skill_process_automation_audit",),
        variables_necesarias=(
            "frecuencia",
            "tiempo_dedicado",
            "personas_involucradas",
            "archivos_usados",
            "flujo_operativo",
        ),
        evidencia_requerida=(
            "descripcion_flujo",
            "archivos_excel",
            "capturas_pantalla",
            "pasos_del_proceso",
            "frecuencia_tarea",
            "responsables",
        ),
        preguntas_mayeuticas=(
            "¿Qué tarea se repite?",
            "¿Cada cuánto se hace?",
            "¿Cuántas personas intervienen?",
            "¿Qué archivos o sistemas usan?",
            "¿Dónde suelen aparecer errores?",
            "¿Tenés una descripción del flujo de trabajo manual?",
        ),
        criterios_para_avanzar=(
            "existe descripción del flujo",
            "existe frecuencia o tiempo estimado",
            "existe evidencia mínima del proceso",
        ),
        criterios_de_bloqueo=(
            "no se describe el flujo",
            "no se identifica tarea concreta",
        ),
    ),
    "incertidumbre_costo_produccion": SymptomEntry(
        symptom_id="incertidumbre_costo_produccion",
        nombre="Incertidumbre sobre costo real de producción",
        dolores_asociados=(
            "no sé si gano plata produciendo esto",
            "no sé cuánto me cuesta fabricar",
            "no tengo claro el costo de materia prima",
            "no sé si el precio final está bien",
            "no sé si conviene producirlo",
            "no tengo armado el cálculo de producción",
        ),
        sintoma_operativo="Falta de claridad sobre costo unitario real, margen productivo o precio final.",
        patologias_posibles=(
            "BOM_incompleto",
            "costos_indirectos_no_imputados",
            "materia_prima_sin_costo_actualizado",
            "mano_obra_no_considerada",
            "merma_productiva_no_contemplada",
            "precio_final_desalineado",
        ),
        hipotesis_template="Investigar si el producto {producto} tiene costo de producción completo y margen suficiente considerando materia prima, mano de obra, merma y costos indirectos.",
        skills_candidatas=("skill_bom_cost_audit",),
        variables_necesarias=(
            "producto",
            "lista_materiales",
            "cantidades_por_producto",
            "costo_unitario_materiales",
            "mano_obra",
            "merma",
            "precio_final",
        ),
        evidencia_requerida=(
            "receta_o_BOM",
            "facturas_materia_prima",
            "lista_costos",
            "hoja_produccion",
            "precio_venta",
            "tiempos_produccion",
        ),
        preguntas_mayeuticas=(
            "¿Qué producto querés revisar?",
            "¿Tenés lista de materiales o receta?",
            "¿Tenés costos unitarios de materia prima?",
            "¿Querés incluir mano de obra, merma y costos indirectos?",
            "¿Tenés precio final de venta?",
            "¿Tenés los tiempos de producción del producto?",
        ),
        criterios_para_avanzar=(
            "existe producto",
            "existe al menos lista de materiales o costos de materia prima",
            "existe precio final o margen esperado",
        ),
        criterios_de_bloqueo=(
            "no hay producto definido",
            "no hay materiales ni costos",
        ),
    ),
}

def list_symptoms() -> Tuple[str, ...]:
    return tuple(SYMPTOM_PATHOLOGY_CATALOG.keys())

def get_symptom(symptom_id: str) -> Optional[SymptomEntry]:
    return SYMPTOM_PATHOLOGY_CATALOG.get(symptom_id)

def require_symptom(symptom_id: str) -> SymptomEntry:
    entry = get_symptom(symptom_id)
    if entry is None:
        raise KeyError(f"Symptom ID '{symptom_id}' not found in catalog.")
    return entry

def get_candidate_pathologies(symptom_id: str) -> Tuple[str, ...]:
    entry = get_symptom(symptom_id)
    return entry.patologias_posibles if entry else ()

def get_candidate_skills(symptom_id: str) -> Tuple[str, ...]:
    entry = get_symptom(symptom_id)
    return entry.skills_candidatas if entry else ()

def get_required_variables(symptom_id: str) -> Tuple[str, ...]:
    entry = get_symptom(symptom_id)
    return entry.variables_necesarias if entry else ()

def get_required_evidence(symptom_id: str) -> Tuple[str, ...]:
    entry = get_symptom(symptom_id)
    return entry.evidencia_requerida if entry else ()

def get_mayeutic_questions(symptom_id: str) -> Tuple[str, ...]:
    entry = get_symptom(symptom_id)
    return entry.preguntas_mayeuticas if entry else ()
