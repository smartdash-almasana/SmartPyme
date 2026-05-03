from app.catalogs.skill_registry import SkillRegistry
from app.catalogs.symptom_pathology_catalog import SYMPTOM_CATALOG

def test_all_symptom_skills_exist_in_registry():
    registry = SkillRegistry()
    for sid, data in SYMPTOM_CATALOG.items():
        for skill_id in data.get("candidate_skills", []):
            assert registry.has_skill(skill_id), f"Skill '{skill_id}' usada en síntoma '{sid}' no existe en SkillRegistry"
