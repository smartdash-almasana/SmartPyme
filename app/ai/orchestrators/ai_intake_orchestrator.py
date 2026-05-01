from __future__ import annotations

import logging
from typing import Protocol

from app.ai.consumers.owner_message_soft_interpretation_consumer import (
    OwnerMessageSoftInterpretationConsumer,
)
from app.ai.schemas.soft_interpretation_result import SoftInterpretationResult

logger = logging.getLogger(__name__)


class SoftInterpretationConsumer(Protocol):
    def consume(self, message: str) -> SoftInterpretationResult:
        ...


class AIIntakeOrchestrator:
    """Local AI intake orchestration boundary.

    This is not Hermes Runtime yet.
    It only coordinates the current AI-layer consumer and returns
    the stable SoftInterpretationResult contract.

    Boundary rules:
    - no pipeline integration
    - no persistence
    - no jobs
    - no deterministic-core mutation
    - no business decision
    - no factory imports
    """

    def __init__(self, consumer: SoftInterpretationConsumer | None = None) -> None:
        self._consumer = consumer or OwnerMessageSoftInterpretationConsumer()

    def interpret_owner_message(self, message: str) -> SoftInterpretationResult:
        if not message.strip():
            return SoftInterpretationResult.empty(raw_message=message)

        try:
            result = self._consumer.consume(message)
        except Exception as exc:
            logger.debug("AIIntakeOrchestrator failed: %s", exc)
            return SoftInterpretationResult.failed(
                raw_message=message,
                errors=["orchestrator_exception"],
            )

        if isinstance(result, SoftInterpretationResult):
            return result

        return SoftInterpretationResult.failed(
            raw_message=message,
            errors=["invalid_orchestrator_output"],
        )
