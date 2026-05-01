from factory.adapters.app_bridge.agent_loop.models import AgentLoopContext, AgentLoopResult
from factory.adapters.app_bridge.agent_loop.service import run_agent_loop
from app.orchestrator.multiagent.models import DirectorPlan
from app.orchestrator.skills.registry import SkillRegistry


def execute_plan(
    plan: DirectorPlan,
    registry: SkillRegistry | None = None,
) -> AgentLoopResult:
    if plan.status != "ok":
        return AgentLoopResult(
            status="blocked",
            executed_skills=[],
            final_state=plan.initial_state,
            final_output=None,
            error_code=plan.error_code or "PLAN_NOT_EXECUTABLE",
            error_message=plan.error_message or "El plan no puede ejecutarse.",
        )

    context = AgentLoopContext(
        current_state=plan.initial_state,
        flags=plan.flags,
        payload=plan.initial_payload,
        last_output={},
        executed_skills=[],
    )
    return run_agent_loop(context, registry=registry)
