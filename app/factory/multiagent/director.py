from app.factory.multiagent.models import DirectorPlan, DirectorRequest


def create_plan(request: DirectorRequest) -> DirectorPlan:
    if not request.objetivo.strip():
        return DirectorPlan(
            status="blocked",
            objetivo=request.objetivo,
            initial_state="BLOCKED",
            initial_payload=dict(request.payload_inicial),
            flags=dict(request.flags),
            error_code="OBJETIVO_INVALIDO",
            error_message="El objetivo no puede estar vacio.",
        )

    return DirectorPlan(
        status="ok",
        objetivo=request.objetivo,
        initial_state="CREATED",
        initial_payload=dict(request.payload_inicial),
        flags=dict(request.flags),
        error_code=None,
        error_message=None,
    )
