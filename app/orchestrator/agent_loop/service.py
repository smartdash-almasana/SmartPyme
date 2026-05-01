from app.orchestrator.agent_loop.models import AgentLoopContext, AgentLoopResult
from app.orchestrator.router.models import RouterContext
from app.orchestrator.router.service import decide_next_skill
from app.orchestrator.skills.registry import SkillRegistry
from app.orchestrator.skills.runner import run_skill

MAX_STEPS = 10

STATE_BY_SKILL: dict[str, str] = {
    "echo_skill": "AFTER_ECHO",
    "wrap_echo_skill": "AFTER_WRAP",
}


def _blocked(
    executed_skills: list[str],
    final_state: str,
    final_output: dict | None,
    error_code: str,
    error_message: str,
) -> AgentLoopResult:
    return AgentLoopResult(
        status="blocked",
        executed_skills=executed_skills,
        final_state=final_state,
        final_output=final_output,
        error_code=error_code,
        error_message=error_message,
    )


def run_agent_loop(
    context: AgentLoopContext,
    registry: SkillRegistry | None = None,
) -> AgentLoopResult:
    current_state = context.current_state
    payload = dict(context.payload)
    last_output = dict(context.last_output)
    executed_skills = list(context.executed_skills)

    for _ in range(MAX_STEPS):
        router_context = RouterContext(
            current_state=current_state,
            flags=context.flags,
            last_output=last_output,
        )
        decision = decide_next_skill(router_context)

        if decision.status == "done":
            return AgentLoopResult(
                status="done",
                executed_skills=executed_skills,
                final_state=current_state,
                final_output=last_output or None,
                error_code=None,
                error_message=None,
            )

        if decision.status == "blocked":
            return _blocked(
                executed_skills=executed_skills,
                final_state=current_state,
                final_output=last_output or None,
                error_code=decision.error_code or "NO_ROUTE_FOUND",
                error_message=decision.reason,
            )

        if not decision.next_skill_id:
            return _blocked(
                executed_skills=executed_skills,
                final_state=current_state,
                final_output=last_output or None,
                error_code="NO_ROUTE_FOUND",
                error_message="El router no devolvio un next_skill_id valido.",
            )

        skill_result = run_skill(decision.next_skill_id, payload, registry=registry)
        if skill_result["status"] == "error":
            return _blocked(
                executed_skills=executed_skills,
                final_state=current_state,
                final_output=last_output or None,
                error_code=skill_result.get("error_code") or "SKILL_EXECUTION_ERROR",
                error_message=skill_result.get("error_message") or "Fallo la ejecucion del skill.",
            )

        executed_skills.append(decision.next_skill_id)
        last_output = skill_result["output"]
        payload = skill_result["output"]

        next_state = STATE_BY_SKILL.get(decision.next_skill_id)
        if not next_state:
            return _blocked(
                executed_skills=executed_skills,
                final_state=current_state,
                final_output=last_output,
                error_code="STATE_TRANSITION_NOT_FOUND",
                error_message=(
                    "No existe transicion de estado para skill: "
                    f"{decision.next_skill_id}"
                ),
            )
        current_state = next_state

    return _blocked(
        executed_skills=executed_skills,
        final_state=current_state,
        final_output=last_output or None,
        error_code="MAX_STEPS_EXCEEDED",
        error_message="Se alcanzo el maximo de pasos del agent loop.",
    )
