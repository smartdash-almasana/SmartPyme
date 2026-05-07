from fastapi import APIRouter
from app.api.v1.endpoints import jobs, laboratorio_p0

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(laboratorio_p0.router, prefix="/laboratorio/p0", tags=["laboratorio"])
