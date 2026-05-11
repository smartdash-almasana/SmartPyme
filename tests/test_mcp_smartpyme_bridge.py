"""
Tests: bem_submit_workflow MCP tool.

NOTA DE COBERTURA:
bem_submit_workflow importa BemClient, BemRunRepository, BemSubmitService y
CuratedEvidenceRepositoryBackend localmente dentro de la función, sin seam de
inyección de dependencias. Forzar patches sobre imports locales es frágil y
viola el contrato de no-hack de tests.

Cobertura real del flujo completo (BEM response → CuratedEvidenceRecord):
  - BemSubmitService: tests/services/test_bem_submit_service_curated_evidence.py
  - HTTP router:      tests/api/test_bem_submit_router.py
  - Adapter:          tests/services/test_bem_curated_evidence_adapter.py

Este archivo cubre únicamente comportamientos observables del tool MCP
sin llamadas reales a BEM:
  - REJECTED por tenant_id vacío
  - REJECTED por workflow_id vacío
  - REJECTED por payload vacío
  - Estructura de respuesta REJECTED
"""
from __future__ import annotations

import asyncio

import pytest


# ---------------------------------------------------------------------------
# Tests de validación de input — no requieren BEM real ni patches frágiles
# ---------------------------------------------------------------------------


def test_mcp_bem_submit_workflow_rejected_tenant_vacio() -> None:
    """tenant_id vacío produce REJECTED con error controlado."""
    from mcp_smartpyme_bridge import bem_submit_workflow

    result = asyncio.run(
        bem_submit_workflow(
            tenant_id="",
            workflow_id="wf-1",
            payload={"x": 1},
        )
    )

    assert result["status"] == "REJECTED"
    assert result["source"] == "real"
    assert "reason" in result


def test_mcp_bem_submit_workflow_rejected_workflow_vacio() -> None:
    """workflow_id vacío produce REJECTED con error controlado."""
    from mcp_smartpyme_bridge import bem_submit_workflow

    result = asyncio.run(
        bem_submit_workflow(
            tenant_id="tenant-a",
            workflow_id="",
            payload={"x": 1},
        )
    )

    assert result["status"] == "REJECTED"
    assert result["source"] == "real"
    assert "reason" in result


def test_mcp_bem_submit_workflow_rejected_payload_vacio() -> None:
    """payload vacío produce REJECTED con error controlado."""
    from mcp_smartpyme_bridge import bem_submit_workflow

    result = asyncio.run(
        bem_submit_workflow(
            tenant_id="tenant-a",
            workflow_id="wf-1",
            payload={},
        )
    )

    assert result["status"] == "REJECTED"
    assert result["source"] == "real"
    assert "reason" in result


def test_mcp_bem_submit_workflow_rejected_sin_api_key() -> None:
    """Sin BEM_API_KEY real, el tool retorna REJECTED sin propagar excepción."""
    from mcp_smartpyme_bridge import bem_submit_workflow

    result = asyncio.run(
        bem_submit_workflow(
            tenant_id="tenant-a",
            workflow_id="wf-1",
            payload={"x": 1},
        )
    )

    # Sin API key real, BemClient falla → REJECTED controlado
    assert result["status"] == "REJECTED"
    assert result["source"] == "real"
    assert "error_type" in result
    assert "reason" in result
