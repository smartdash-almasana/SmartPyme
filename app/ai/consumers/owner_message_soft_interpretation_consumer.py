from __future__ import annotations

import logging
from typing import Protocol

from app.ai.adapters.owner_message_interpreter_adapter import LocalOwnerMessageInterpreterAdapter
from app.ai.schemas.soft_interpretation_result import SoftInterpretationResult

logger = logging.getLogger(__name__)


class SoftInterpretationAdapter(Protocol):
    def interpret_result(self, message: str) -> SoftInterpretationResult:
        ...


class OwnerMessageSoftInterpretationConsumer:
    """Internal consumer for soft owner-message interpretation.

    Boundary rule:
    - consumes the local AI adapter result contract
    - returns only SoftInterpretationResult
    - does not persist
    - does not create jobs
    - does not call pipeline
    - does not decide business actions
    """

    def __init__(self, adapter: SoftInterpretationAdapter | None = None) -> None:
        self._adapter = adapter or LocalOwnerMessageInterpreterAdapter()

    def consume(self, message: str) -> SoftInterpretationResult:
        if not message.strip():
            return SoftInterpretationResult.empty(raw_message=message)

        try:
            result = self._adapter.interpret_result(message)
        except Exception as exc:
            logger.debug("OwnerMessageSoftInterpretationConsumer failed: %s", exc)
            return SoftInterpretationResult.failed(
                raw_message=message,
                errors=["consumer_exception"],
            )

        if isinstance(result, SoftInterpretationResult):
            return result

        return SoftInterpretationResult.failed(
            raw_message=message,
            errors=["invalid_consumer_output"],
        )
