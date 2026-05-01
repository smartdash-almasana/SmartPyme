from app.orchestrator.router.models import RouterContext, RoutingDecision


def _blocked(reason: str) -> RoutingDecision:
    return RoutingDecision(
        status="blocked",
        next_skill_id=None,
        reason=reason,
        error_code="NO_ROUTE_FOUND",
    )


def decide_next_skill(context: RouterContext) -> RoutingDecision:
    if context.current_state == "CREATED" and context.flags.get("needs_echo") is True:
        return RoutingDecision(
            status="ok",
            next_skill_id="echo_skill",
            reason="Regla 1 aplicada: CREATED + needs_echo=True.",
            error_code=None,
        )

    if context.current_state == "AFTER_ECHO" and "echoed_message" in context.last_output:
        return RoutingDecision(
            status="ok",
            next_skill_id="wrap_echo_skill",
            reason="Regla 2 aplicada: AFTER_ECHO con echoed_message disponible.",
            error_code=None,
        )

    if context.current_state == "AFTER_WRAP":
        return RoutingDecision(
            status="done",
            next_skill_id=None,
            reason="Regla 3 aplicada: flujo finalizado en AFTER_WRAP.",
            error_code=None,
        )

    return _blocked("No existe una regla de ruteo valida para el contexto recibido.")
