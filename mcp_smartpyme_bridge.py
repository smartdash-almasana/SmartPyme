import asyncio
from mcp.server.fastmcp import FastMCP

# Inicialización del servidor MCP para SmartPyme
mcp = FastMCP("SmartPyme-Bridge")

@mcp.tool()
async def get_job_status(job_id: str) -> dict:
    """
    Consulta el estado actual de un Job en el JobEngine.
    Utilizar cuando el usuario pregunte 'cómo va la tarea X'.
    """
    # Stub: Aquí se importará el JobEngine en la fase 2
    # Por ahora emulamos la respuesta del motor determinístico
    mock_database = {
        "JOB-MARIO-001": {"status": "IN_PROGRESS", "progress": "65%", "step": "fiscal_reconciliation", "client": "Mario S.A."},
        "JOB-MARIO-002": {"status": "COMPLETED", "progress": "100%", "step": "reconciliation", "client": "Mario S.A."}
    }
    
    return mock_database.get(job_id, {"status": "NOT_FOUND"})

@mcp.tool()
async def list_pending_validations(owner_id: str) -> list[dict]:
    """
    Lista validaciones pendientes que requieren atención humana.
    """
    # Stub: Aquí se conectará con el EvidenceSystem en la fase 2
    return [
        {
            "id": "VAL-MS-201",
            "type": "human_validation",
            "description": "Confirmar si la factura duplicada #9928 de Mario S.A. es un error de carga o una nota de crédito.",
            "status": "AWAITING_VALIDATION"
        },
        {
            "id": "VAL-MS-202",
            "type": "clarification",
            "description": "Falta adjunto de retención IIBB para el periodo 03/2024 de Mario S.A.",
            "status": "AWAITING_VALIDATION"
        },
        {
            "id": "VAL-MS-203",
            "type": "conflict_resolution",
            "description": "Discrepancia entre saldo bancario y arqueo de caja en sucursal Mario S.A. Centro.",
            "status": "AWAITING_VALIDATION"
        }
    ]

@mcp.tool()
async def get_evidence(evidence_id: str) -> dict:
    """
    Recupera los detalles de una evidencia específica (factura, remito, log).
    Utilizar cuando el usuario pida 'mostrame la factura' o 'dame el detalle del error'.
    """
    # Stub: Aquí se conectará con el EvidenceSystem en la fase 2
    mock_evidence_store = {
        "VAL-MS-201": {
            "id": "VAL-MS-201",
            "filename": "factura_9928_duplicada.pdf",
            "metadata": {"amount": 1500.50, "date": "2024-03-15", "issuer": "Vendor Corp"},
            "verification_hash": "sha256:e3b0c442..."
        }
    }
    
    return mock_evidence_store.get(evidence_id, {"error": "EVIDENCE_NOT_FOUND"})

if __name__ == "__main__":
    # El servidor corre por defecto en modo stdio para ser consumido por Hermes
    mcp.run()