import pytest
from app.catalogs.skill_operational_conditions import SkillOperationalConditionsRegistry


def test_all_skills_have_conditions():
    registry = SkillOperationalConditionsRegistry()
    skill_ids = registry.list_skill_ids()
    assert len(skill_ids) == 5

    for sid in skill_ids:
        conditions = registry.get_conditions(sid)
        assert conditions.skill_id == sid
        assert len(conditions.required_variables) > 0
        assert len(conditions.required_evidence) > 0
        assert len(conditions.blocking_conditions) > 0


def test_invalid_skill_conditions():
    registry = SkillOperationalConditionsRegistry()
    with pytest.raises(ValueError):
        registry.get_conditions("non_existent_skill")
