"""Orquestador de aplicación P0 para Laboratorio de Análisis PyME MVP.

Coordina LaboratorioService + LaboratorioPersistenceContext para ejecutar
el flujo P0 mínimo: crear caso diagnóstico y persistir las entidades core
(Job + OperationalCase) en el proveedor configurado.

Principios:
    - No decide negocio automáticamente.
    - No persiste LaboratorioReportDraft como entidad propia.
    - No inventa contratos paralelos.
    - Fail-closed si falta persistence_context.
    - cliente_id fluye a través de todas las entidades creadas.
    - job_id se preserva si se provee; se genera uno si no.

CONTRACT_BRIDGE:
    LaboratorioPymeCase (Laboratorio) → OperationalCase (core P0)
        case_id         → case_id
        cliente_id      → cliente_id
        job_id          → job_id
        laboratorios[0] → skill_id (primer laboratorio como skill orientativo)
        dueno_nombre    → hypothesis (prefijo "Investigar si..." para cumplir contrato)
        estado          → status ("OPEN")

    Job (core P0):
        job_id          → job_id (generado si no se provee)
        cliente_id      → cliente_id
        job_type        → "LABORATORIO_MVP"
        status          → JobStatus.PENDING

    LaboratorioReportDraft NO se persiste — es transiente por diseño.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from app.contracts.job_contract import Job, JobStatus
from app.contracts.operational_case import OperationalCase
from app.laboratorio_pyme.contracts import LaboratorioPymeCase
from app.laboratorio_pyme.persistence import LaboratorioPersistenceContext
from app.laboratorio_pyme.service import LaboratorioService
from app.laboratorio_pyme.tipos import TipoLaboratorio


@dataclass(frozen=True, slots=True)
class CasoPersistenteResult:
    """Resultado del flujo crear_caso_persistente.

    Contiene los IDs de las entidades core creadas y persistidas.
    """

    cliente_id: str
    case_id: str
    job_id: str
    laboratorio_case: LaboratorioPymeCase


class LaboratorioApplicationService:
    """Orquestador fino de aplicación para el Laboratorio MVP.

    Coordina LaboratorioService (lógica de dominio del Laboratorio) con
    LaboratorioPersistenceContext (repositorios P0) para ejecutar el flujo
    mínimo persistible.

    Args:
        laboratorio_service: Instancia de LaboratorioService. Obligatorio.
        persistence_context: Instancia de LaboratorioPersistenceContext.
            Obligatorio. Fail-closed si es None.

    Raises:
        ValueError: Si persistence_context es None.
    """

    def __init__(
        self,
        laboratorio_service: LaboratorioService,
        persistence_context: LaboratorioPersistenceContext,
    ) -> None:
        if persistence_context is None:
            raise ValueError(
                "persistence_context is required. "
                "Proveer un LaboratorioPersistenceContext válido."
            )
        self._service = laboratorio_service
        self._ctx = persistence_context

    def crear_caso_persistente(
        self,
        cliente_id: str,
        dueno_nombre: str,
        laboratorios: list[TipoLaboratorio],
        *,
        job_id: str | None = None,
        user_id: str | None = None,
    ) -> CasoPersistenteResult:
        """Crea un caso diagnóstico y persiste Job + OperationalCase en P0.

        Flujo:
            1. Genera job_id si no se provee.
            2. Crea Job core (status=PENDING, job_type=LABORATORIO_MVP).
            3. Persiste Job en ctx.jobs.
            4. Crea LaboratorioPymeCase via LaboratorioService.
            5. Proyecta LaboratorioPymeCase → OperationalCase core P0.
            6. Persiste OperationalCase en ctx.operational_cases.
            7. Devuelve CasoPersistenteResult con IDs creados.

        LaboratorioReportDraft NO se persiste — es transiente por diseño.

        Args:
            cliente_id: Identificador del tenant. Obligatorio.
            dueno_nombre: Nombre del dueño de la PyME. Obligatorio.
            laboratorios: Lista de laboratorios seleccionados. Obligatorio.
            job_id: ID de job existente. Si None, se genera uno nuevo.
            user_id: Enlace opcional al usuario que inició el flujo.

        Returns:
            CasoPersistenteResult con cliente_id, case_id, job_id y el
            LaboratorioPymeCase creado.
        """
        # 1. Resolver job_id
        resolved_job_id = job_id or str(uuid.uuid4())

        # 2. Crear Job core P0
        job = Job(
            job_id=resolved_job_id,
            cliente_id=cliente_id,
            job_type="LABORATORIO_MVP",
            status=JobStatus.PENDING,
            payload={
                "dueno_nombre": dueno_nombre,
                "laboratorios": [lab.value for lab in laboratorios],
            },
            traceable_origin={"source": "laboratorio_application_service"},
        )

        # 3. Persistir Job
        self._ctx.jobs.create(job)

        # 4. Crear LaboratorioPymeCase via LaboratorioService
        laboratorio_case = self._service.crear_caso(
            cliente_id=cliente_id,
            dueno_nombre=dueno_nombre,
            laboratorios=laboratorios,
            job_id=resolved_job_id,
            user_id=user_id,
        )

        # 5. Proyectar LaboratorioPymeCase → OperationalCase core P0
        #    CONTRACT_BRIDGE: skill_id = primer laboratorio seleccionado.
        #    hypothesis debe ser investigable (prefijo "Investigar si...").
        skill_id = laboratorios[0].value if laboratorios else "laboratorio_pyme"
        hypothesis = (
            f"Investigar si {dueno_nombre} presenta síntomas detectables "
            f"en {skill_id}?"
        )

        op_case = OperationalCase(
            cliente_id=cliente_id,
            case_id=laboratorio_case.case_id,
            job_id=resolved_job_id,
            skill_id=skill_id,
            hypothesis=hypothesis,
            evidence_ids=[],
            status="OPEN",
        )

        # 6. Persistir OperationalCase
        self._ctx.operational_cases.create_case(op_case)

        # 7. Devolver resultado
        return CasoPersistenteResult(
            cliente_id=cliente_id,
            case_id=laboratorio_case.case_id,
            job_id=resolved_job_id,
            laboratorio_case=laboratorio_case,
        )
