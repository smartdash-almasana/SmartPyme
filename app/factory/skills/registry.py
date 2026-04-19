from app.factory.skills.builtin import get_builtin_skills
from app.factory.skills.models import SkillSpec


class SkillNotFoundError(ValueError):
    pass


class SkillDisabledError(ValueError):
    pass


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, SkillSpec] = {}

    @classmethod
    def load_builtin(cls) -> "SkillRegistry":
        registry = cls()
        for skill in get_builtin_skills():
            registry._skills[skill.skill_id] = skill
        return registry

    def get_skill(self, skill_id: str) -> SkillSpec:
        skill = self._skills.get(skill_id)
        if skill is None:
            raise SkillNotFoundError(f"Skill not found: {skill_id}")
        if not skill.enabled:
            raise SkillDisabledError(f"Skill is disabled: {skill_id}")
        return skill

    def list_skills(self) -> list[SkillSpec]:
        return list(self._skills.values())

    def set_skill(self, skill: SkillSpec) -> None:
        self._skills[skill.skill_id] = skill
