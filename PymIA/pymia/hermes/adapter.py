"""
adapter.py — Adapter Hermes ↔ ClinicalConversationalPort (offline).

RESPONSABILIDAD
===============
Este módulo traduce el vocabulario de Hermes (message_text, metadata,
reply_text, payload) al vocabulario del port clínico (text, message,
anamnesis, laboratorio) — y viceversa.

No contiene lógica clínica. No contiene lógica de Hermes.
Solo adapta contratos.

POSICIÓN EN LA ARQUITECTURA
----------------------------

    Hermes (externo, futuro)
        │
        │  HermesInput(tenant_id, channel, message_text, metadata)
        ▼
    HermesAdapter.handle()
        │  [traducción de vocabulario — sin lógica clínica]
        │
        │  ConversationalInput(tenant_id, channel, text)
        ▼
    ClinicalConversationalPort.handle()
        │  [kernel clínico — sin conocimiento de Hermes]
        │
        │  ConversationalOutput(status, mode, message, anamnesis, laboratorio)
        ▼
    HermesAdapter.handle()
        │  [traducción de vuelta — sin interpretar el kernel]
        │
        │  HermesOutput(status, mode, reply_text, payload)
        ▼
    Hermes (externo, futuro)

EJEMPLO DE INTEGRACIÓN FUTURA
------------------------------
Cuando el runtime Hermes real esté listo, la integración se reduce a:

    from pymia.hermes.adapter import HermesAdapter, HermesInput

    adapter = HermesAdapter()
    output = adapter.handle(
        HermesInput(
            tenant_id=session.tenant_id,
            channel=message.channel,         # "telegram", "whatsapp", etc.
            message_text=message.text,
            metadata={"message_id": message.id, "user_id": message.from_id},
        )
    )

    if output.status == "ok":
        await hermes.reply(output.reply_text)
        # output.payload disponible para trazabilidad / logs, NO para jobs
    else:
        await hermes.ask_for_more_context()

INVARIANTES DEL ADAPTER
------------------------
1. HermesInput.metadata es opaco para el kernel: se recibe, se preserva
   en el payload de salida para trazabilidad, pero NUNCA se interpreta
   como instrucción clínica ni como parámetro de orquestación.

2. HermesOutput.payload es solo lectura para Hermes.
   Contiene anamnesis + laboratorio para logging/auditoría.
   Hermes NO debe usar payload para crear jobs, workflows ni tareas.

3. El adapter no conoce:
   - create_job, workflow, authorization, orchestration, decision_type.
   - El modelo de lenguaje (LLM) ni su runtime.
   - El runtime de Hermes (MCP, YAML config, tool whitelist).
   - La infraestructura de Telegram u otro canal.

4. El adapter es stateless e idempotente.

5. reply_text es None si status != "ok".
   Hermes decide qué hacer en ese caso sin consultar a PymIA.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from pymia.interfaces.conversational_port import (
    ClinicalConversationalPort,
    ConversationalInput,
)
from pymia.services.initial_laboratory_anamnesis_service import (
    AnamnesisOriginaria,
    LaboratorioInicialContrato,
)


# ---------------------------------------------------------------------------
# Contratos Hermes
# ---------------------------------------------------------------------------


class HermesInput(BaseModel):
    """
    Entrada en vocabulario Hermes.

    Campos
    ------
    tenant_id:
        Identificador del tenant. Obligatorio. Multi-tenant.

    channel:
        Canal de mensajería Hermes (ej: "telegram", "whatsapp", "api").
        El adapter lo propaga sin interpretación.

    message_text:
        Texto libre del mensaje recibido por Hermes.
        Se mapea directamente a ConversationalInput.text.

    metadata:
        Diccionario opaco de contexto Hermes (message_id, user_id,
        timestamp, etc.). El kernel clínico NUNCA lo lee.
        Se preserva en HermesOutput.payload para trazabilidad.
    """

    tenant_id: str = Field(..., description="Identificador del tenant.")
    channel: str = Field(..., description="Canal Hermes de origen.")
    message_text: str = Field(
        ...,
        description="Texto del mensaje recibido por Hermes.",
        min_length=1,
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Contexto opaco de Hermes. Solo trazabilidad. "
            "El kernel clínico nunca lo lee."
        ),
    )


class HermesPayload(BaseModel):
    """
    Payload estructurado de salida.

    Contiene la información clínica generada por el kernel, disponible
    para logging/auditoría de Hermes. NO debe usarse para crear jobs
    ni para tomar decisiones de orquestación.
    """

    anamnesis: AnamnesisOriginaria | None = Field(
        None,
        description="Anamnesis originaria. Solo lectura.",
    )
    laboratorio: LaboratorioInicialContrato | None = Field(
        None,
        description="Contrato del laboratorio clínico. Solo lectura.",
    )
    input_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata original de HermesInput, preservada para trazabilidad.",
    )


class HermesOutput(BaseModel):
    """
    Salida en vocabulario Hermes.

    Campos
    ------
    status:
        'ok'        → señal clínica detectada; reply_text listo para enviar.
        'no_signal' → sin señal clínica; Hermes decide cómo continuar.
        'error'     → fallo interno (no debería ocurrir en condiciones normales).

    mode:
        'anamnesis_inicial' → primer tiempo lógico activado.
        'no_signal'         → sin modo clínico activo.

    reply_text:
        Texto listo para enviar al usuario a través de Hermes.
        None si status != 'ok'. Hermes NO debe modificarlo.

    payload:
        Información clínica estructurada para logging/auditoría.
        Hermes NO debe interpretarlo como instrucción de acción.
    """

    status: Literal["ok", "no_signal", "error"] = Field(
        ...,
        description="Estado del procesamiento.",
    )
    mode: Literal["anamnesis_inicial", "no_signal"] = Field(
        ...,
        description="Modo clínico activado.",
    )
    reply_text: str | None = Field(
        None,
        description="Texto listo para enviar. None si no hay señal clínica.",
    )
    payload: HermesPayload = Field(
        default_factory=HermesPayload,
        description="Payload estructurado para trazabilidad. Solo lectura para Hermes.",
    )


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class HermesAdapter:
    """
    Adapter offline Hermes ↔ ClinicalConversationalPort.

    Responsabilidades
    -----------------
    - Traducir HermesInput → ConversationalInput (vocabulario Hermes → vocabulario clínico).
    - Llamar a ClinicalConversationalPort.handle().
    - Traducir ConversationalOutput → HermesOutput (vocabulario clínico → vocabulario Hermes).
    - Preservar metadata de Hermes en el payload de salida.

    Prohibiciones explícitas
    ------------------------
    - No interpreta metadata. No toma decisiones basadas en metadata.
    - No crea jobs, workflows, ni tareas de orquestación.
    - No importa ni referencia el runtime de Hermes real.
    - No conoce MCP, YAML de configuración ni tool whitelist.
    - No modifica reply_text antes de devolverlo.
    - No persiste estado (stateless).
    """

    def __init__(self) -> None:
        # Única dependencia: el puerto clínico soberano.
        # Sin servicios de factoría, MCP, jobs ni orchestration.
        self._port = ClinicalConversationalPort()

    def handle(self, hermes_input: HermesInput) -> HermesOutput:
        """
        Adapta una entrada Hermes y retorna una salida Hermes.

        El flujo interno es:
            HermesInput → ConversationalInput → [kernel] → ConversationalOutput → HermesOutput

        Args:
            hermes_input: Mensaje recibido por Hermes.

        Returns:
            HermesOutput con reply_text listo para enviar y payload para trazabilidad.
        """
        # — Traducción entrada: vocabulario Hermes → vocabulario clínico —
        # metadata es opaco: se guarda para el payload, nunca se pasa al kernel.
        clinical_input = ConversationalInput(
            tenant_id=hermes_input.tenant_id,
            channel=hermes_input.channel,
            text=hermes_input.message_text,
        )

        # — Delegación al kernel clínico —
        clinical_output = self._port.handle(clinical_input)

        # — Construcción del payload de trazabilidad —
        payload = HermesPayload(
            anamnesis=clinical_output.anamnesis,
            laboratorio=clinical_output.laboratorio,
            input_metadata=hermes_input.metadata,
        )

        # — Traducción salida: vocabulario clínico → vocabulario Hermes —
        return HermesOutput(
            status=clinical_output.status,
            mode=clinical_output.mode,
            reply_text=clinical_output.message,
            payload=payload,
        )
