import pytest
from app.catalogs.domain_pack_registry import DomainPackRegistry
from unittest.mock import patch

def test_domain_pack_registry_pyme_latam():
    registry = DomainPackRegistry()
    pack = registry.get_pack("pyme_latam")
    assert pack.domain_id == "pyme_latam"
    assert len(pack.skills) == 5
    assert "skill_margin_leak_audit" in pack.skills

def test_invalid_pack():
    registry = DomainPackRegistry()
    with pytest.raises(ValueError):
        registry.get_pack("non_existent")

def test_missing_skill_validation():
    # Mocking SkillRegistry.has_skill to return False for a skill present in the definition
    with patch('app.catalogs.skill_registry.SkillRegistry.has_skill', return_value=False):
        with pytest.raises(ValueError, match="not found in SkillRegistry"):
            DomainPackRegistry()
