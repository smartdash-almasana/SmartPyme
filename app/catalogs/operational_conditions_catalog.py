from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SkillOperationalConditions:
    skill_id: str
    required_variables: tuple[str, ...] = field(default_factory=tuple)
    required_evidence: tuple[str, ...] = field(default_factory=tuple)
    blocking_rules: tuple[str, ...] = field(default_factory=tuple)


# Catálogo determinístico de condiciones operativas por skill_id
OPERATIONAL_CONDITIONS_CATALOG: dict[str, SkillOperationalConditions] = {
    "skill_reconcile_bank_vs_pos": SkillOperationalConditions(
        skill_id="skill_reconcile_bank_vs_pos",
        required_variables=("pos_total", "bank_total", "periodo"),
        required_evidence=("pos_report", "bank_statement"),
    ),
    "skill_margin_leak_audit": SkillOperationalConditions(
        skill_id="skill_margin_leak_audit",
        required_variables=("markup_objetivo", "costo_reposicion"),
        required_evidence=("supplier_invoices", "pos_sales"),
    ),
    "skill_stock_loss_detect": SkillOperationalConditions(
        skill_id="skill_stock_loss_detect",
        required_variables=("stock_teorico", "ajuste_merma"),
        required_evidence=("inventory_log", "pos_sales"),
    ),
}
