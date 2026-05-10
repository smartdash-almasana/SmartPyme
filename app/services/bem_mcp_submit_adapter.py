from __future__ import annotations

from typing import Any, Protocol


class McpToolCaller(Protocol):
    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        ...


class BemMcpSubmitAdapter:
    def __init__(self, mcp_client: McpToolCaller, tool_name: str = "bem_submit_workflow") -> None:
        self._mcp_client = mcp_client
        self._tool_name = tool_name

    def submit_payload(
        self,
        workflow_id: str,
        payload: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        tenant_id = kwargs.get("tenant_id")
        call_reference_id = kwargs.get("call_reference_id")

        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id is required")
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise ValueError("workflow_id is required")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload is required")
        if call_reference_id is not None and (
            not isinstance(call_reference_id, str) or not call_reference_id.strip()
        ):
            raise ValueError("call_reference_id is invalid")

        params: dict[str, Any] = {
            "tenant_id": tenant_id.strip(),
            "workflow_id": workflow_id.strip(),
            "payload": payload,
        }
        if call_reference_id is not None:
            params["call_reference_id"] = call_reference_id

        result = self._mcp_client.call_tool(self._tool_name, **params)
        if not isinstance(result, dict):
            raise RuntimeError("invalid MCP response")

        status = result.get("status")
        if status == "COMPLETED":
            response_payload = result.get("response_payload")
            if response_payload is not None and not isinstance(response_payload, dict):
                raise RuntimeError("invalid MCP response_payload")
            return response_payload or result

        error_type = result.get("error_type") or "BEM_UPSTREAM_ERROR"
        reason = result.get("reason") or "unknown MCP failure"
        raise RuntimeError(f"{error_type}: {reason}")
