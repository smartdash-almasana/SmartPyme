from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SkillOperationalConditions:
    skill_id: str
    required_variables: List[str]
    required_evidence: List[str]
    blocking_conditions: List[str]

class SkillOperationalConditionsRegistry:
    def __init__(self):
        self._conditions: Dict[str, SkillOperationalConditions] = {
            "skill_margin_leak_audit": SkillOperationalConditions(
                skill_id="skill_margin_leak_audit",
                required_variables=["margin_threshold", "period"],
                required_evidence=["sales_report", "cost_report"],
                blocking_conditions=["missing_margin_threshold", "missing_period_data"]
            ),
            "skill_stock_loss_detect": SkillOperationalConditions(
                skill_id="skill_stock_loss_detect",
                required_variables=["inventory_id"],
                required_evidence=["stock_logs", "physical_count"],
                blocking_conditions=["missing_inventory_id", "missing_physical_count"]
            ),
            "skill_reconcile_bank_vs_pos": SkillOperationalConditions(
                skill_id="skill_reconcile_bank_vs_pos",
                required_variables=["bank_id", "pos_id"],
                required_evidence=["bank_statement", "pos_report"],
                blocking_conditions=["missing_bank_statement", "missing_pos_report"]
            ),
            "skill_process_automation_audit": SkillOperationalConditions(
                skill_id="skill_process_automation_audit",
                required_variables=["process_id"],
                required_evidence=["process_logs", "config_files"],
                blocking_conditions=["missing_process_logs", "missing_config_files"]
            ),
            "skill_bom_cost_audit": SkillOperationalConditions(
                skill_id="skill_bom_cost_audit",
                required_variables=["bom_id"],
                required_evidence=["bom_structure", "item_costs"],
                blocking_conditions=["missing_bom_structure", "missing_item_costs"]
            ),
        }

    def get_conditions(self, skill_id: str) -> SkillOperationalConditions:
        if skill_id not in self._conditions:
            raise ValueError(f"Conditions for skill {skill_id} not found")
        return self._conditions[skill_id]
