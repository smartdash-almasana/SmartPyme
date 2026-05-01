from typing import Any

from app.orchestrator.multiagent.director import create_plan
from app.orchestrator.multiagent.executor import execute_plan
from app.orchestrator.multiagent.models import DirectorRequest
from app.orchestrator.skills.registry import SkillRegistry


def run_multiagent_flow(
    request: DirectorRequest,
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    plan = create_plan(request)
    if plan.status != "ok":
        return {
            "status": "blocked",
            "objetivo": plan.objetivo,
            "plan_status": plan.status,
            "executed_skills": [],
            "final_state": plan.initial_state,
            "final_output": None,
            "error_code": plan.error_code,
            "error_message": plan.error_message,
        }

    result = execute_plan(plan, registry=registry)
    return {
        "status": "done" if result.status == "done" else "blocked",
        "objetivo": plan.objetivo,
        "plan_status": plan.status,
        "executed_skills": result.executed_skills,
        "final_state": result.final_state,
        "final_output": result.final_output,
        "error_code": result.error_code,
        "error_message": result.error_message,
    }
