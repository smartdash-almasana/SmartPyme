from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class SkillDefinition:
    skill_id: str
    name: str
    required_variables: List[str]
    required_evidence: List[str]
    output_contract: str
    domain_id: Optional[str] = None

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, SkillDefinition] = {
            "skill_margin_leak_audit": SkillDefinition(
                skill_id="skill_margin_leak_audit",
                name="Margin Leak Audit",
                required_variables=["margin_threshold", "period"],
                required_evidence=["sales_report", "cost_report"],
                output_contract="MarginLeakReport"
            ),
            "skill_stock_loss_detect": SkillDefinition(
                skill_id="skill_stock_loss_detect",
                name="Stock Loss Detection",
                required_variables=["inventory_id"],
                required_evidence=["stock_logs", "physical_count"],
                output_contract="StockLossAnalysis"
            ),
            "skill_reconcile_bank_vs_pos": SkillDefinition(
                skill_id="skill_reconcile_bank_vs_pos",
                name="Bank vs POS Reconciliation",
                required_variables=["bank_id", "pos_id"],
                required_evidence=["bank_statement", "pos_report"],
                output_contract="ReconciliationResult"
            ),
            "skill_process_automation_audit": SkillDefinition(
                skill_id="skill_process_automation_audit",
                name="Process Automation Audit",
                required_variables=["process_id"],
                required_evidence=["process_logs", "config_files"],
                output_contract="AutomationAuditReport"
            ),
            "skill_bom_cost_audit": SkillDefinition(
                skill_id="skill_bom_cost_audit",
                name="BOM Cost Audit",
                required_variables=["bom_id"],
                required_evidence=["bom_structure", "item_costs"],
                output_contract="BOMCostAnalysis"
            ),
        }

    def get_skill(self, skill_id: str) -> Optional[SkillDefinition]:
        return self._skills.get(skill_id)

    def has_skill(self, skill_id: str) -> bool:
        return skill_id in self._skills

    def list_skills(self) -> List[SkillDefinition]:
        return list(self._skills.values())
