from __future__ import annotations

import logging
from collections.abc import Callable

from app.ai.agents.owner_message_interpreter_agent import interpret_owner_message_with_ai
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation

logger = logging.getLogger(__name__)

OwnerMessageInterpreter = Callable[[str], OwnerMessageInterpretation | None]


class LocalOwnerMessageInterpreterAdapter:
    """Local adapter for the soft owner-message interpreter.

    Boundary rule:
    - the adapter may ask the soft interpreter for an interpretation
    - the adapter never decides, persists, schedules jobs, or mutates core state
    - the adapter always returns a validated OwnerMessageInterpretation
    """

    def __init__(
        self,
        interpreter: OwnerMessageInterpreter | None = None,
    ) -> None:
        self._interpreter = interpreter or interpret_owner_message_with_ai

    def interpret(self, message: str) -> OwnerMessageInterpretation:
        if not message.strip():
            return self.empty()

        try:
            interpretation = self._interpreter(message)
        except Exception as exc:
            logger.debug("LocalOwnerMessageInterpreterAdapter failed: %s", exc)
            return self.empty()

        if isinstance(interpretation, OwnerMessageInterpretation):
            return interpretation

        return self.empty()

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
