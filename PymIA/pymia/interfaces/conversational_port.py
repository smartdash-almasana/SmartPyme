"""
conversational_port.py — Puerto de entrada conversacional clínica de PymIA.

BOUNDARY CONTRACT
=================
Este módulo define la única superficie pública que una interfaz externa
(Hermes, Telegram, API REST, CLI, etc.) puede tocar para hablar con
el kernel clínico de PymIA.

INVARIANTES DEL BOUNDARY
-------------------------
1. El port acepta SOLO (tenant_id, channel, text).
   No recibe: job_id, workflow_id, authorization_token, decision_type,
   create_job, orchestration_context ni ningún artefacto de factoría.

2. El port devuelve SOLO (status, mode, message, anamnesis, laboratorio).
   No devuelve: job_created, workflow_step, authorization_result,
   approval_required ni ningún artefacto de orquestación.

3. El port NO contiene lógica clínica. Delega siempre al kernel.
   La lógica clínica vive en:
     pymia.pipeline.admission.v1
     pymia.services.initial_laboratory_anamnesis_service

4. El port es stateless. No persiste, no cachea, no acumula estado.

5. El port no conoce el modelo de lenguaje, el runtime de Hermes
   ni la infraestructura de mensajería.

EJEMPLO DE INTEGRACIÓN FUTURA (Hermes → PymIA)
-----------------------------------------------
Cuando Hermes reciba un mensaje de Telegram, deberá llamar al port
de esta manera — y SOLO de esta manera:

    from pymia.interfaces.conversational_port import (
        ClinicalConversationalPort,
        ConversationalInput,
    )

    port = ClinicalConversationalPort()
    output = port.handle(
        ConversationalInput(
            tenant_id=session.tenant_id,
            channel="telegram",
            text=message.text,
        )
    )

    if output.status == "ok":
        await bot.send_message(chat_id, output.message)
    else:
        # Sin señal clínica: Hermes decide qué hacer (no PymIA)
        await bot.send_message(chat_id, "Contame más sobre tu negocio.")

Lo que Hermes NO debe hacer:
    - Pasar job_id al port.
    - Interpretar output.anamnesis para crear workflows.
    - Escalar a orchestration si status != "ok".
    - Modificar output.message antes de enviarlo.

DIAGRAMA DE FLUJO
-----------------
Hermes (interfaz)
    │
    │  ConversationalInput(tenant_id, channel, text)
    ▼
ClinicalConversationalPort.handle()
    │
    │  (delega, sin lógica propia)
    ▼
InitialLaboratoryAnamnesisService.process()
    │
    ├── AdmissionPipelineV1.run()
    │       └── heuristics.get_hypotheses_for_claim()
    └── AdmissionResponseFormatterV1.format_response()
    │
    ▼
ConversationalOutput(status, mode, message, anamnesis, laboratorio)
    │
    ▼
Hermes (solo entrega el mensaje; no interpreta el kernel)
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from pymia.services.initial_laboratory_anamnesis_service import (
    AnamnesisOriginaria,
    InitialLaboratoryAnamnesisService,
    LaboratorioInicialContrato,
)


# ---------------------------------------------------------------------------
# Contratos de entrada y salida del port
# ---------------------------------------------------------------------------


class ConversationalInput(BaseModel):
    """
    Entrada al puerto conversacional clínico.

    Contiene únicamente la información mínima de contexto conversacional.
    No incluye ningún artefacto de orquestación, autorización o factoría.
    """

    tenant_id: str = Field(
        ...,
        description="Identificador del tenant (dueño de PyME). Multi-tenant obligatorio.",
    )
    channel: str = Field(
        ...,
        description=(
            "Canal de entrada (ej: 'telegram', 'api', 'cli'). "
            "El port no cambia su comportamiento según el canal; "
            "el canal es solo trazabilidad."
        ),
    )
    text: str = Field(
        ...,
        description="Texto libre del dueño. El kernel lo interpreta de forma determinística.",
        min_length=1,
    )


class ConversationalOutput(BaseModel):
    """
    Salida del puerto conversacional clínico.

    Contiene únicamente información clínica estructurada.
    No incluye job_id, workflow_step, authorization_result ni decision_type.

    Campos
    ------
    status:
        'ok'        → se detectó una señal clínica y se generó respuesta.
        'no_signal' → el texto no activó ningún patrón clínico conocido.
        'error'     → fallo interno del kernel (no debería ocurrir en condiciones normales).

    mode:
        'anamnesis_inicial' → primer tiempo lógico: síntomas + hipótesis + evidencia.
        'no_signal'         → sin señal; el modo conversacional lo decide la interfaz externa.

    message:
        Texto listo para entregar al dueño. Sin procesamiento adicional.
        None si status != 'ok'.

    anamnesis:
        Estructura clínica interna. La interfaz externa PUEDE loguearla
        pero NO debe alterarla ni usarla para crear jobs o workflows.

    laboratorio:
        Contrato del primer laboratorio clínico abierto.
        La interfaz externa PUEDE mostrarlo pero NO debe interpretarlo
        como una orden de ejecución automática.
    """

    status: Literal["ok", "no_signal", "error"] = Field(
        ...,
        description="Estado del procesamiento clínico.",
    )
    mode: Literal["anamnesis_inicial", "no_signal"] = Field(
        ...,
        description="Modo clínico activado.",
    )
    message: str | None = Field(
        None,
        description="Mensaje sobrio listo para el dueño. None si no hay señal.",
    )
    anamnesis: AnamnesisOriginaria | None = Field(
        None,
        description="Estructura de anamnesis originaria. Solo lectura para la interfaz.",
    )
    laboratorio: LaboratorioInicialContrato | None = Field(
        None,
        description="Contrato del laboratorio inicial abierto. Solo lectura para la interfaz.",
    )


# ---------------------------------------------------------------------------
# Puerto conversacional clínico
# ---------------------------------------------------------------------------


class ClinicalConversationalPort:
    """
    Puerto de entrada conversacional para el kernel clínico de PymIA.

    Responsabilidades
    -----------------
    - Recibir (tenant_id, channel, text) desde cualquier interfaz externa.
    - Delegar al kernel clínico sin modificar ni interpretar su salida.
    - Devolver un ConversationalOutput estructurado y limpio.

    Prohibiciones explícitas
    ------------------------
    Este port NUNCA debe:
    - Crear jobs, workflows ni tareas de orquestación.
    - Verificar autorización o permisos de Hermes.
    - Conocer el runtime de Hermes, el modelo LLM o la infraestructura MCP.
    - Tomar decisiones clínicas (eso es responsabilidad del kernel).
    - Persistir estado (es stateless por diseño).

    Garantías
    ---------
    - El output.message es siempre apto para entrega directa al dueño.
    - Si status == 'no_signal', la interfaz externa decide cómo continuar
      la conversación; PymIA no da instrucciones al respecto.
    - El port es idempotente: el mismo input produce el mismo output.
    """

    def __init__(self) -> None:
        # El servicio clínico es la única dependencia del port.
        # No se inyectan servicios de factoría, MCP, jobs ni orchestration.
        self._service = InitialLaboratoryAnamnesisService()

    def handle(self, input: ConversationalInput) -> ConversationalOutput:
        """
        Procesa una entrada conversacional y retorna la respuesta clínica.

        Este método es el único punto de entrada al kernel clínico desde
        cualquier interfaz externa. No debe ser extendido para añadir
        lógica de jobs, workflows ni orquestación.

        Args:
            input: ConversationalInput con tenant_id, channel y text.

        Returns:
            ConversationalOutput con status, mode, message, anamnesis y laboratorio.
        """
        # BOUNDARY CHECK: todo lo que llega aquí es solo texto conversacional.
        # Si en el futuro alguien intenta añadir job_id o workflow_context
        # a esta firma, es una violación de boundary y debe ser rechazada.

        result = self._service.process(
            tenant_id=input.tenant_id,
            channel=input.channel,
            text=input.text,
        )

        if result is None:
            # Sin señal clínica detectada.
            # La interfaz externa decide qué hacer; PymIA no prescribe acciones.
            return ConversationalOutput(
                status="no_signal",
                mode="no_signal",
                message=None,
                anamnesis=None,
                laboratorio=None,
            )

        # Señal clínica detectada: primer tiempo lógico de anamnesis.
        return ConversationalOutput(
            status="ok",
            mode="anamnesis_inicial",
            message=result.message,
            anamnesis=result.anamnesis,
            laboratorio=result.laboratorio,
        )
