from dataclasses import dataclass
from typing import Dict, List

from app.catalogs.skill_registry import SkillRegistry


@dataclass
class SkillOperationalConditions:
    skill_id: str
    required_variables: List[str]
    required_evidence: List[str]
    blocking_conditions: List[str]


class SkillOperationalConditionsRegistry:
    def __init__(self):
        self.skill_registry = SkillRegistry()
        self._conditions: Dict[str, SkillOperationalConditions] = {
            "skill_margin_leak_audit": SkillOperationalConditions(
                skill_id="skill_margin_leak_audit",
                required_variables=["periodo", "margen_esperado"],
                required_evidence=["ventas_pos", "facturas_proveedor"],
                blocking_conditions=["falta_periodo", "falta_evidencia_ventas"],
            ),
            "skill_stock_loss_detect": SkillOperationalConditions(
                skill_id="skill_stock_loss_detect",
                required_variables=["periodo", "stock_fisico"],
                required_evidence=["inventario_fisico", "reporte_movimientos"],
                blocking_conditions=["falta_inventario_fisico"],
            ),
            "skill_reconcile_bank_vs_pos": SkillOperationalConditions(
                skill_id="skill_reconcile_bank_vs_pos",
                required_variables=["periodo", "saldo_banco"],
                required_evidence=["extracto_bancario", "reporte_pos"],
                blocking_conditions=["falta_extracto_bancario", "falta_reporte_pos"],
            ),
            "skill_process_automation_audit": SkillOperationalConditions(
                skill_id="skill_process_automation_audit",
                required_variables=["proceso", "horas_hombre"],
                required_evidence=["diagrama_proceso", "bitacora_tareas"],
                blocking_conditions=["falta_descripcion_proceso"],
            ),
            "skill_bom_cost_audit": SkillOperationalConditions(
                skill_id="skill_bom_cost_audit",
                required_variables=["producto", "costos_indirectos"],
                required_evidence=["receta_produccion", "facturas_insumos"],
                blocking_conditions=["falta_producto", "falta_receta_produccion"],
            ),
        }
        self._validate_conditions()

    def _validate_conditions(self) -> None:
        for skill_id, conditions in self._conditions.items():
            if not self.skill_registry.has_skill(skill_id):
                raise ValueError(f"Skill {skill_id} not found in SkillRegistry")
            if conditions.skill_id != skill_id:
                raise ValueError(f"Skill condition key mismatch for {skill_id}")
            if not conditions.required_variables:
                raise ValueError(f"Skill {skill_id} missing required_variables")
            if not conditions.required_evidence:
                raise ValueError(f"Skill {skill_id} missing required_evidence")
            if not conditions.blocking_conditions:
                raise ValueError(f"Skill {skill_id} missing blocking_conditions")

    def get_conditions(self, skill_id: str) -> SkillOperationalConditions:
        if skill_id not in self._conditions:
            raise ValueError(f"Conditions for skill {skill_id} not found")
        return self._conditions[skill_id]

    def list_skill_ids(self) -> list[str]:
        return list(self._conditions.keys())
