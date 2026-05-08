from __future__ import annotations

import os
import pathlib

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.laboratorio_pyme.p0_runner import run_laboratorio_p0

router = APIRouter()

_FORM_HTML = (
    pathlib.Path(__file__).parent.parent.parent.parent
    / "laboratorio_pyme"
    / "templates"
    / "p0_form.html"
)


@router.get("/form", response_class=HTMLResponse, include_in_schema=False)
def laboratorio_p0_form() -> HTMLResponse:
    """Formulario web mínimo para ejecutar el flujo Laboratorio P0."""
    return HTMLResponse(content=_FORM_HTML.read_text(encoding="utf-8"))


class LaboratorioP0Request(BaseModel):
    cliente_id: str
    dueno_nombre: str
    laboratorio: str
    hallazgo: str


@router.post("/casos")
def create_caso(payload: LaboratorioP0Request):
    try:
        result = run_laboratorio_p0(
            cliente_id=payload.cliente_id,
            dueno_nombre=payload.dueno_nombre,
            laboratorio=payload.laboratorio,
            hallazgo=payload.hallazgo,
            load_env_local=True,
        )
        return result.to_dict()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="No se pudo ejecutar el flujo Laboratorio P0. Revisar configuración y evidencia.",
        ) from exc


@router.get("/reportes/{report_id}")
def get_reporte(report_id: str, cliente_id: str):
    """Consulta un report persistido por report_id y cliente_id."""
    from app.laboratorio_pyme.persistence import LaboratorioPersistenceContext
    from app.repositories.persistence_provider import PersistenceProvider, get_provider

    provider = get_provider(os.environ.get("SMARTPYME_PERSISTENCE_PROVIDER"))

    supabase_client = None
    if provider == PersistenceProvider.SUPABASE:
        from app.laboratorio_pyme.p0_runner import _build_supabase_client_from_env
        supabase_client = _build_supabase_client_from_env()

    try:
        ctx = LaboratorioPersistenceContext.from_repository_factory(
            cliente_id=cliente_id,
            provider=provider.value,
            supabase_client=supabase_client,
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=503,
            detail="Proveedor de persistencia no disponible para reportes.",
        )

    report = ctx.reports.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")

    response: dict = {
        "cliente_id": report.cliente_id,
        "report_id": report.report_id,
        "case_id": getattr(report, "case_id", None),
        "status": getattr(report, "diagnosis_status", None),
    }
    for field in ("payload", "result", "metadata"):
        val = getattr(report, field, None)
        if val is not None:
            response[field] = val

    return response
