from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

AdapterResultStatus = Literal["executed", "blocked", "failed"]


@dataclass(frozen=True, slots=True)
class ExecutionAdapterResult:
    adapter_id: str
    action_id: str
    status: AdapterResultStatus         # "executed" | "blocked" | "failed"
    message: str
    traceable_origin: dict[str, Any] = field(default_factory=dict)


class ExecutionAdapter(ABC):
    """
    Abstract base for execution adapters.
    Concrete implementations (e.g. HermesAdapter) live outside SmartPyme core.
    SmartPyme decides; the adapter executes.
    """

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Unique identifier for this adapter (e.g. 'hermes', 'mock')."""

    @abstractmethod
    def execute(self, proposal: Any) -> ExecutionAdapterResult:
        """
        Attempt to execute the given ActionProposal.
        Must return an ExecutionAdapterResult.
        Must NOT raise — failures must be expressed via status='failed'.
        """
