from __future__ import annotations

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
