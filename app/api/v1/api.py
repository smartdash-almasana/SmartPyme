from fastapi import APIRouter
from app.api.v1.endpoints import jobs, laboratorio_p0, laboratorio_tabular
from app.api.bem_webhook_router import router as bem_webhook_router
from app.api.diagnostic_router import router as diagnostic_router

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(laboratorio_p0.router, prefix="/laboratorio/p0", tags=["laboratorio"])
api_router.include_router(
    laboratorio_tabular.router,
    prefix="/laboratorio/tabular",
    tags=["laboratorio-tabular"],
)
api_router.include_router(bem_webhook_router, tags=["bem"])
api_router.include_router(diagnostic_router, tags=["diagnostico"])
