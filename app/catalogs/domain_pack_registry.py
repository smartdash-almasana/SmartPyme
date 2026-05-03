from dataclasses import dataclass
from typing import List
from app.catalogs.skill_registry import SkillRegistry

@dataclass
class DomainPackDefinition:
    domain_id: str
    skills: List[str]

class DomainPackRegistry:
    def __init__(self):
        self.skill_registry = SkillRegistry()
        self._packs = {
            "pyme_latam": DomainPackDefinition(
                domain_id="pyme_latam",
                skills=[
                    "skill_margin_leak_audit",
                    "skill_stock_loss_detect",
                    "skill_reconcile_bank_vs_pos",
                    "skill_process_automation_audit",
                    "skill_bom_cost_audit"
                ]
            )
        }

    def get_pack(self, domain_id: str) -> DomainPackDefinition:
        if domain_id not in self._packs:
            raise ValueError(f"Domain pack {domain_id} not found")
        return self._packs[domain_id]
