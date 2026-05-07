"""Servicio orquestador mínimo del Laboratorio de Análisis PyME MVP.

No decide negocio automáticamente.
Organiza evidencia y crea estructuras para revisión humana.

Los identificadores core de SmartPyme (job_id, decision_id, user_id) son
opcionales y se pasan a través de los contratos cuando se proveen.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.laboratorio_pyme.contracts import (
    DiagnosticFinding,
    LaboratorioPymeCase,
    LaboratorioReportDraft,
    LaboratorioSelection,
)
from app.laboratorio_pyme.tipos import TipoLaboratorio


class LaboratorioService:
    """
    Orquestador mínimo del flujo diagnóstico del Laboratorio de Análisis PyME.

    Crea y gestiona el ciclo de vida de un caso diagnóstico.
    No decide negocio automáticamente — organiza evidencia para revisión humana.
    El cliente_id fluye a través de todos los contratos creados.
    Los identificadores core (job_id, decision_id, user_id) se preservan
    cuando se proveen — no se generan ni transforman.
    """

    def crear_caso(
        self,
        cliente_id: str,
        dueno_nombre: str,
        laboratorios: list[TipoLaboratorio],
        *,
        job_id: str | None = None,
        user_id: str | None = None,
    ) -> LaboratorioPymeCase:
        """Crea un caso diagnóstico en estado 'borrador'.

        Args:
            cliente_id: Identificador del tenant/cliente. Obligatorio.
            dueno_nombre: Nombre del dueño de la PyME. Obligatorio.
            laboratorios: Lista de laboratorios seleccionados. Obligatorio.
            job_id: Enlace opcional al job core de SmartPyme.
            user_id: Enlace opcional al usuario que inició el flujo.
        """
        return LaboratorioPymeCase(
            cliente_id=cliente_id,
            case_id=str(uuid.uuid4()),
            dueno_nombre=dueno_nombre,
            laboratorios=laboratorios,
            estado="borrador",
            creado_en=datetime.now(tz=timezone.utc).isoformat(),
            job_id=job_id,
            user_id=user_id,
        )

    def crear_selection(
        self,
        cliente_id: str,
        case_id: str,
        laboratorios: list[TipoLaboratorio],
        *,
        job_id: str | None = None,
    ) -> LaboratorioSelection:
        """Registra formalmente la selección de laboratorios para un caso.

        Args:
            cliente_id: Identificador del tenant/cliente. Obligatorio.
            case_id: Identificador del caso. Obligatorio.
            laboratorios: Lista de laboratorios seleccionados. Obligatorio.
            job_id: Enlace opcional al job core de SmartPyme.
        """
        return LaboratorioSelection(
            cliente_id=cliente_id,
            case_id=case_id,
            laboratorios_seleccionados=laboratorios,
            job_id=job_id,
        )

    def crear_borrador_informe(
        self,
        cliente_id: str,
        case_id: str,
        hallazgos: list[DiagnosticFinding],
        *,
        job_id: str | None = None,
        decision_id: str | None = None,
        user_id: str | None = None,
    ) -> LaboratorioReportDraft:
        """Crea un borrador de informe agregando los hallazgos recibidos.

        El borrador es un objeto transiente — no se persiste directamente.

        Args:
            cliente_id: Identificador del tenant/cliente. Obligatorio.
            case_id: Identificador del caso. Obligatorio.
            hallazgos: Lista de hallazgos a incluir en el borrador.
            job_id: Enlace opcional al job core de SmartPyme.
            decision_id: Enlace opcional a la decisión asociada.
            user_id: Enlace opcional al usuario que generó el borrador.
        """
        return LaboratorioReportDraft(
            cliente_id=cliente_id,
            report_id=str(uuid.uuid4()),
            case_id=case_id,
            hallazgos=hallazgos,
            estado_borrador="pendiente_revision",
            generado_en=datetime.now(tz=timezone.utc).isoformat(),
            job_id=job_id,
            decision_id=decision_id,
            user_id=user_id,
        )
