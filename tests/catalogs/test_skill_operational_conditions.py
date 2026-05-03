import pytest
from app.catalogs.skill_operational_conditions import SkillOperationalConditionsRegistry

def test_skill_conditions_registry():
    registry = SkillOperationalConditionsRegistry()
    conditions = registry.get_conditions("skill_margin_leak_audit")
    assert conditions.skill_id == "skill_margin_leak_audit"
    assert "margin_threshold" in conditions.required_variables
    assert len(conditions.blocking_conditions) >= 1

def test_invalid_skill_conditions():
    registry = SkillOperationalConditionsRegistry()
    with pytest.raises(ValueError):
        registry.get_conditions("non_existent_skill")
