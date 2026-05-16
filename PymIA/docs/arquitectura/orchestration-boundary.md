# Hermes Producto — Boundary de Orquestación

## Estado

Documento complementario canónico de `hermes/arquitectura-conversacional.md`.

## Regla obligatoria

Hermes Producto / Hermes SmartPyme es obligatorio en el flujo conversacional del producto.

Telegram es solamente canal de entrada y salida.

BEM, Curated Evidence y SmartPyme Kernel son capacidades internas orquestadas por Hermes Producto.

## Flujo correcto

```text
Telegram
→ Hermes Producto
→ AI Layer
→ Pydantic
→ BEM / Curated Evidence, si corresponde
→ SmartPyme Kernel
→ Hallazgos
→ Hermes Producto
→ Telegram
```

## Flujo incorrecto

```text
Telegram → BEM
Telegram → SmartPyme Kernel
Telegram → Diagnóstico
```

Cualquier documento que permita leer esos atajos queda reemplazado por esta frontera.

## Criterio

Si Hermes Producto no está en el camino, el flujo no pertenece a la arquitectura oficial de SmartPyme Producto.

## Regla de soberanía del kernel

Hermes Producto no crea jobs por defecto.

Hermes Producto no decide diagnósticos fuera del kernel.

Hermes Producto no inventa findings.

```text
La IA interpreta.
El kernel SmartPyme decide.
```

## Boundary de herramientas MCP

Las herramientas MCP disponibles para Hermes Producto en el contexto conversacional con el dueño son:

```text
PERMITIDAS:
- get_job_status
- list_pending_validations
- resolve_clarification
- save_clarification
- get_evidence
- ingest_document
- bem_submit_workflow

PROHIBIDAS en el flujo conversacional inicial:
- create_job
- factory_process_intake
- factory_confirm_intake
- factory_start_authorized_job
- factory_build_operational_case
```

Un mensaje PyME inicial no puede crear jobs.

El flujo correcto para un mensaje inicial es:

```text
Telegram update
→ TelegramAdapter.handle_update()
→ _handle_conversational_message()
→ InitialLaboratoryAnamnesisService.process()
→ anamnesis_inicial / hipótesis / evidencia requerida
```
