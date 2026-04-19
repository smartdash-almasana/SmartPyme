from app.factory.orchestrator.models import (
    STATE_BLOCKED,
    STATE_COMPLETED,
    STATE_CREATED,
    STATE_RUNNING,
)


class InvalidTransitionError(ValueError):
    pass


ALLOWED_TRANSITIONS: set[tuple[str, str]] = {
    (STATE_CREATED, STATE_RUNNING),
    (STATE_RUNNING, STATE_COMPLETED),
    (STATE_RUNNING, STATE_BLOCKED),
}


def ensure_transition_allowed(from_state: str, to_state: str) -> None:
    if (from_state, to_state) not in ALLOWED_TRANSITIONS:
        raise InvalidTransitionError(
            f"Transicion invalida: {from_state} -> {to_state}"
        )
