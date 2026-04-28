# SmartPyme OS actual

## Estado de este documento

Este documento fue reconciliado el 2026-04-28 para alinearse con `docs/factory/FACTORY_CONTRATO_OPERATIVO.md` y `docs/factory/RUNTIME_VIGENTE.md`.

La verdad operativa vigente es:

```text
Hermes Gateway externo = runtime conversacional
SmartPyme repo = fuente de verdad, contratos, TaskSpecs, gates y evidencia
factory/hermes_control_cli.py = adaptador interno permitido
```

Los runners `scripts/hermes_factory_runner.py`, `scripts/telegram_factory_control.py` y `run_sfma_cycle.sh` quedan clasificados como `LEGACY_DEPRECATED / PROHIBIDO / NO OPERATIVO` para producción.

## Verdad operativa

SmartPyme es el sistema de verdad del dominio operativo. Guarda estado, evidencias, clarificaciones, contratos, TaskSpecs y gates. No es el operador conversacional ni debe contener un cerebro autónomo de producción.

Hermes Agent / Hermes Gateway es el operador conversacional externo. Recibe la conversación con el usuario y llama herramientas MCP o adaptadores cuando necesita leer o modificar estado de SmartPyme.

MCP es el contrato de borde entre Hermes y SmartPyme. La integración activa para tools MCP está en `mcp_smartpyme_bridge.py`.

## Runtime vigente de factoría

El runtime vigente de la factoría es **Hermes Gateway externo**.

El adaptador interno permitido es:

```text
factory/hermes_control_cli.py
```

La cola activa versionada para unidades de trabajo es:

```text
factory/ai_governance/tasks/*.yaml
```

El gate de ciclo y estado operativo se registran en:

```text
factory/control/AUDIT_GATE.md
factory/control/FACTORY_STATUS.md
```

`factory/hallazgos/*` no es la cola activa de factoría. Cualquier uso de esas rutas debe tratarse como antecedente histórico, dominio de negocio pendiente de contrato explícito o material legacy.

## Runners legacy no operativos

Los siguientes artefactos no deben ser ejecutados por systemd, GitHub Actions, Hermes Gateway ni scripts de operación:

```text
scripts/hermes_factory_runner.py
scripts/telegram_factory_control.py
run_sfma_cycle.sh
```

Si aparecen en documentación activa, deben figurar únicamente como `LEGACY`, `DEPRECATED`, `PROHIBIDO` o `NO OPERATIVO`.

## Roles

| componente | rol actual | no gobierna |
|---|---|---|
| Hermes Gateway | Operador conversacional externo | Persistencia, reglas de negocio, verdad de jobs |
| MCP | Contrato de tools entre Hermes y SmartPyme | Arquitectura conceptual del core |
| SmartPyme | Sistema de verdad, persistencia, contratos, TaskSpecs y evidencia | Interfaz conversacional principal |
| `factory/hermes_control_cli.py` | Adaptador interno invocable por Hermes Gateway | Runtime autónomo, loop propio o auditoría final |
| Codex | Builder externo bajo TaskSpec | Roadmap, arquitectura y auditoría final |
| Gemini | Auditor técnico externo | Builder productivo por defecto |
| ChatGPT | Auditor/director externo bajo evidencia | Ejecución autónoma de ciclos |

## Capas reales evidenciadas

| capa | estado | archivo principal | observación |
|---|---|---|---|
| Bridge MCP | implementado y validado | `mcp_smartpyme_bridge.py` | Expone tools reales por stdio para Hermes. |
| Jobs | implementado mínimo | `app/factory/orchestrator/persistence.py` | SQLite real en `data/jobs.db`; persiste estado, `skill_id` y `payload_json`. |
| Orquestación de jobs | implementado mínimo | `app/factory/orchestrator/service.py` | Persiste transiciones `CREATED -> RUNNING -> COMPLETED/BLOCKED`. |
| Clarifications | implementado y validado | `app/core/clarification/persistence.py` | CRUD mínimo real en SQLite. |
| EvidenceStore | implementado mínimo | `services/document_ingestion_service.py` | JSONL local para documentos y chunks. |
| Ingesta documental | implementado y validado por bridge | `services/document_ingestion_service.py` | `ingest_document` usa el servicio y devuelve evidencias. |
| Consulta de evidencia | implementado y validado por bridge | `mcp_smartpyme_bridge.py` | Lee `evidence_store/document_chunks/chunks.jsonl`. |
| Reconciliation | implementado parcialmente | `app/core/reconciliation/service.py` | Hay servicio y tests, pero no está expuesto por MCP. |
| Hallazgos | implementado parcialmente | `app/core/hallazgos/service.py` | Existe dominio, pero no gobierna aún el runtime MCP. |
| Normalización / canonical rows | conceptual pendiente | no evidenciado como runtime cerrado | Debe separarse de ingesta y reconciliation. |
| Entity resolution | conceptual pendiente | no evidenciado como runtime cerrado | No debe darse por cerrado. |
| Action engine | conceptual pendiente | no evidenciado | No hay contrato operativo MCP activo. |

## Persistencias reales

| persistencia | archivo / ubicación | uso actual |
|---|---|---|
| Jobs SQLite | `data/jobs.db` | Estado de jobs consultado por `get_job_status`. |
| Clarifications SQLite | `data/clarifications.db` | Clarificaciones pendientes y resueltas. |
| EvidenceStore JSONL | `evidence_store/document_chunks/chunks.jsonl` | Chunks consultables por `get_evidence`. |
| Raw documents JSONL | `evidence_store/raw_documents/documents.jsonl` | Documentos ingestados. |
| Citation index JSON | `evidence_store/citation_index/citations.json` | Índice liviano de citas. |

## Tools MCP activas

| tool | estado | backend real | observación |
|---|---|---|---|
| `get_job_status` | implementada | `app.factory.orchestrator.persistence.get_job` | Devuelve `source: real`; `NOT_FOUND` si no existe. |
| `create_job` | implementada | `app.contracts.operational_plan_contract.create_operational_plan` + `app.factory.orchestrator.persistence.save_job` | Crea plan declarativo y job en `CREATED`; persiste `skill_id` y payload del plan. |
| `list_pending_validations` | implementada | `app.core.clarification.persistence.list_pending_clarifications` | `owner_id` existe en contrato, aún no filtra. |
| `resolve_clarification` | implementada | `app.core.clarification.persistence.resolve_clarification` | Resuelve pendientes en SQLite. |
| `save_clarification` | implementada | `app.core.clarification.persistence.save_clarification` | Crea clarificación manual bloqueante. |
| `get_evidence` | implementada | JSONL en EvidenceStore | Si falta el store responde `stub_explicit`; con store real lee JSONL. |
| `ingest_document` | implementada | `DocumentIngestionService` | Ingesta archivo local y devuelve `evidence_ids`. |

## Validación E2E existente

La validación E2E está en `tests/e2e/validate_bridge_e2e.py`.

Valida, en un flujo completo:

1. `get_job_status`
2. `save_clarification`
3. `list_pending_validations`
4. `resolve_clarification`
5. confirmación de resolución
6. `ingest_document`
7. `get_evidence`

Comando documentado:

```powershell
python tests/e2e/validate_bridge_e2e.py
```

Advertencia operativa: el script limpia `jobs.db`, `clarifications.db`, el documento temporal E2E y `evidence_store` al finalizar. Debe correrse en entorno de validación o con datos descartables.

## Historial de Cambios

- 2026-04-28 — Reconciliado por remediación P0 / DOC-001. Se eliminó la doble verdad que presentaba `scripts/hermes_factory_runner.py` como runner operativo actual. Se declara Hermes Gateway externo como runtime conversacional vigente y los runners legacy como prohibidos/no operativos.
