from __future__ import annotations

import logging
from collections.abc import Callable

from app.ai.agents.owner_message_interpreter_agent import interpret_owner_message_with_ai
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation
from app.ai.schemas.soft_interpretation_result import SoftInterpretationResult

logger = logging.getLogger(__name__)

OwnerMessageInterpreter = Callable[[str], OwnerMessageInterpretation | None]


class LocalOwnerMessageInterpreterAdapter:
    """Local adapter for the soft owner-message interpreter.

    Boundary rule:
    - the adapter may ask the soft interpreter for an interpretation
    - the adapter never decides, persists, schedules jobs, or mutates core state
    - the adapter can expose either a validated interpretation or a stable result contract
    """

    def __init__(
        self,
        interpreter: OwnerMessageInterpreter | None = None,
    ) -> None:
        self._interpreter = interpreter or interpret_owner_message_with_ai

    def interpret(self, message: str) -> OwnerMessageInterpretation:
        """Backward-compatible interpretation API.

        Returns only the validated interpretation payload.
        Use interpret_result() when status and error metadata are required.
        """

        return self.interpret_result(message).interpretation

    def interpret_result(self, message: str) -> SoftInterpretationResult:
        """Return a stable result contract for local soft interpretation."""

        if not message.strip():
            return SoftInterpretationResult.empty(raw_message=message)

        try:
            interpretation = self._interpreter(message)
        except Exception as exc:
            logger.debug("LocalOwnerMessageInterpreterAdapter failed: %s", exc)
            return SoftInterpretationResult.failed(
                raw_message=message,
                errors=["interpreter_exception"],
            )

        if isinstance(interpretation, OwnerMessageInterpretation):
            if interpretation == self.empty():
                return SoftInterpretationResult.empty(raw_message=message)
            return SoftInterpretationResult.ok(
                raw_message=message,
                interpretation=interpretation,
            )

        return SoftInterpretationResult.failed(
            raw_message=message,
            errors=["invalid_interpreter_output"],
        )

    @staticmethod
    def empty() -> OwnerMessageInterpretation:
        return OwnerMessageInterpretation(
            intent=None,
            entities=[],
            variables=[],
            evidence=[],
            doubts=[],
            confidence=None,
        )
