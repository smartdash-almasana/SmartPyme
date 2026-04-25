# SmartPyme OS actual

## Verdad operativa

SmartPyme es el sistema de verdad del dominio operativo. Guarda estado, evidencias, clarificaciones y ejecuciones. No es el operador conversacional.

Hermes Agent es el operador conversacional. Recibe la conversacion con el usuario y llama tools MCP cuando necesita leer o modificar estado de SmartPyme.

MCP es el contrato de borde entre Hermes y SmartPyme. La integracion activa esta en `mcp_smartpyme_bridge.py`.

## Roles

| componente | rol actual | no gobierna |
|---|---|---|
| Hermes Agent | Operador conversacional y cliente MCP | Persistencia, reglas de negocio, verdad de jobs |
| MCP | Contrato de tools entre Hermes y SmartPyme | Arquitectura conceptual del core |
| SmartPyme | Sistema de verdad, persistencia y servicios | Interfaz conversacional principal |
| Factory | Herramientas de crecimiento, skills y orquestacion interna minima | Runtime conversacional de usuario |

## Capas reales evidenciadas

| capa | estado | archivo principal | observacion |
|---|---|---|---|
| Bridge MCP | implementado y validado | `mcp_smartpyme_bridge.py` | Expone tools reales por stdio para Hermes. |
| Jobs | implementado minimo | `app/factory/orchestrator/persistence.py` | SQLite real en `data/jobs.db`; persiste estado, `skill_id` y `payload_json`. |
| Orquestacion de jobs | implementado minimo | `app/factory/orchestrator/service.py` | Persiste transiciones `CREATED -> RUNNING -> COMPLETED/BLOCKED`. |
| Clarifications | implementado y validado | `app/core/clarification/persistence.py` | CRUD minimo real en SQLite. |
| EvidenceStore | implementado minimo | `services/document_ingestion_service.py` | JSONL local para documentos y chunks. |
| Ingesta documental | implementado y validado por bridge | `services/document_ingestion_service.py` | `ingest_document` usa el servicio y devuelve evidencias. |
| Consulta de evidencia | implementado y validado por bridge | `mcp_smartpyme_bridge.py` | Lee `evidence_store/document_chunks/chunks.jsonl`. |
| Reconciliation | implementado parcialmente | `app/core/reconciliation/service.py` | Hay servicio y tests, pero no esta expuesto por MCP. |
| Hallazgos | implementado parcialmente | `app/core/hallazgos/service.py` | Existe dominio, pero no gobierna aun el runtime MCP. |
| Normalizacion / canonical rows | conceptual pendiente | no evidenciado como runtime cerrado | Debe separarse de ingesta y reconciliation. |
| Entity resolution | conceptual pendiente | no evidenciado como runtime cerrado | No debe darse por cerrado. |
| Action engine | conceptual pendiente | no evidenciado | No hay contrato operativo MCP activo. |

## Persistencias reales

| persistencia | archivo / ubicacion | uso actual |
|---|---|---|
| Jobs SQLite | `data/jobs.db` | Estado de jobs consultado por `get_job_status`. |
| Clarifications SQLite | `data/clarifications.db` | Clarificaciones pendientes y resueltas. |
| EvidenceStore JSONL | `evidence_store/document_chunks/chunks.jsonl` | Chunks consultables por `get_evidence`. |
| Raw documents JSONL | `evidence_store/raw_documents/documents.jsonl` | Documentos ingestados. |
| Citation index JSON | `evidence_store/citation_index/citations.json` | Indice liviano de citas. |

## Tools MCP activas

| tool | estado | backend real | observacion |
|---|---|---|---|
| `get_job_status` | implementada | `app.factory.orchestrator.persistence.get_job` | Devuelve `source: real`; `NOT_FOUND` si no existe. |
| `create_job` | implementada | `app.contracts.operational_plan_contract.create_operational_plan` + `app.factory.orchestrator.persistence.save_job` | Crea plan declarativo y job en `CREATED`; persiste `skill_id` y payload del plan. |
| `list_pending_validations` | implementada | `app.core.clarification.persistence.list_pending_clarifications` | `owner_id` existe en contrato, aun no filtra. |
| `resolve_clarification` | implementada | `app.core.clarification.persistence.resolve_clarification` | Resuelve pendientes en SQLite. |
| `save_clarification` | implementada | `app.core.clarification.persistence.save_clarification` | Crea clarificacion manual bloqueante. |
| `get_evidence` | implementada | JSONL en EvidenceStore | Si falta el store responde `stub_explicit`; con store real lee JSONL. |
| `ingest_document` | implementada | `DocumentIngestionService` | Ingesta archivo local y devuelve `evidence_ids`. |

## Validacion E2E existente

La validacion E2E esta en `tests/e2e/validate_bridge_e2e.py`.

Valida, en un flujo completo:

1. `get_job_status`
2. `save_clarification`
3. `list_pending_validations`
4. `resolve_clarification`
5. confirmacion de resolucion
6. `ingest_document`
7. `get_evidence`

Comando documentado:

```powershell
python tests/e2e/validate_bridge_e2e.py
```

Advertencia operativa: el script limpia `jobs.db`, `clarifications.db`, el documento temporal E2E y `evidence_store` al finalizar. Debe correrse en entorno de validacion o con datos descartables.
