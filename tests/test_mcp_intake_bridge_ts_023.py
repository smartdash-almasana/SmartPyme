from __future__ import annotations

import asyncio
import pytest
from unittest.mock import MagicMock, patch
from mcp_smartpyme_bridge import mcp

def test_factory_process_intake_propagation():
    # We mock AIIntakeOrchestrator to test only the bridge exposure
    with patch("app.ai.orchestrators.ai_intake_orchestrator.AIIntakeOrchestrator") as MockOrchestrator:
        mock_instance = MockOrchestrator.return_value
        expected_output = {
            "status": "JOB_PROPOSAL",
            "job_preview": {
                "cliente_id": "C1",
                "skill_id": "skill_reconcile_bank_vs_pos",
                "objective": "Test objective",
                "intent": "skill_reconcile_bank_vs_pos",
                "summary": "Test summary",
                "raw_message": "test message"
            }
        }
        mock_instance.process_owner_message.return_value = expected_output

        # Call the tool through the bridge logic
        from mcp_smartpyme_bridge import factory_process_intake
        result = asyncio.run(factory_process_intake("test message", "C1"))

        assert result == expected_output
        mock_instance.process_owner_message.assert_called_once_with("test message", "C1")

def test_factory_process_intake_error_handling():
    with patch("app.ai.orchestrators.ai_intake_orchestrator.AIIntakeOrchestrator") as MockOrchestrator:
        mock_instance = MockOrchestrator.return_value
        mock_instance.process_owner_message.side_effect = Exception("System failure")

        from mcp_smartpyme_bridge import factory_process_intake
        result = asyncio.run(factory_process_intake("test message", "C1"))

        assert result["status"] == "REJECTED"
        assert result["error_type"] == "INTERNAL_ERROR"
        assert "System failure" in result["reason"]

def test_bridge_registration():
    async def get_tools():
        return await mcp.list_tools()
    
    tools = asyncio.run(get_tools())
    tool_names = [t.name for t in tools]
    assert "factory_process_intake" in tool_names
