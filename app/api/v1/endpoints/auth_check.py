from fastapi import APIRouter, Depends
from app.api.dependencies import get_active_client

router = APIRouter()


@router.get("/auth/whoami")
async def whoami(cliente_id: str = Depends(get_active_client)):
    return {
        "status": "sovereign",
        "cliente_id": cliente_id
    }
