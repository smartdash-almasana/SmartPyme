from __future__ import annotations

from typing import Any, Protocol


class BemSubmitPort(Protocol):
    def submit_payload(
        self,
        workflow_id: str,
        payload: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        ...
