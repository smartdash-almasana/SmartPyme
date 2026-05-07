"""Servicio orquestador mínimo del Laboratorio de Análisis PyME MVP.

No decide negocio automáticamente.
Organiza evidencia y crea estructuras para revisión humana.
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
    """

    def crear_caso(
        self,
        cliente_id: str,
        dueno_nombre: str,
        laboratorios: list[TipoLaboratorio],
    ) -> LaboratorioPymeCase:
        """Crea un caso diagnóstico en estado 'borrador'."""
        return LaboratorioPymeCase(
            cliente_id=cliente_id,
            case_id=str(uuid.uuid4()),
            dueno_nombre=dueno_nombre,
            laboratorios=laboratorios,
            estado="borrador",
            creado_en=datetime.now(tz=timezone.utc).isoformat(),
        )

    def crear_selection(
        self,
        cliente_id: str,
        case_id: str,
        laboratorios: list[TipoLaboratorio],
    ) -> LaboratorioSelection:
        """Registra formalmente la selección de laboratorios para un caso."""
        return LaboratorioSelection(
            cliente_id=cliente_id,
            case_id=case_id,
            laboratorios_seleccionados=laboratorios,
        )

    def crear_borrador_informe(
        self,
        cliente_id: str,
        case_id: str,
        hallazgos: list[DiagnosticFinding],
    ) -> LaboratorioReportDraft:
        """Crea un borrador de informe agregando los hallazgos recibidos."""
        return LaboratorioReportDraft(
            cliente_id=cliente_id,
            report_id=str(uuid.uuid4()),
            case_id=case_id,
            hallazgos=hallazgos,
            estado_borrador="pendiente_revision",
            generado_en=datetime.now(tz=timezone.utc).isoformat(),
        )
