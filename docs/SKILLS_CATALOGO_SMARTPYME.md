# Catalogo de skills SmartPyme

## Estado de la capa existente

SmartPyme ya tiene una capa tecnica minima de skills en `app/factory/skills`.

Esa capa hoy resuelve ejecucion local de factory:

- `SkillSpec`
- `SkillRegistry`
- `run_skill`
- validacion simple de schemas
- executors builtin
- dos skills de eco: `echo_skill` y `wrap_echo_skill`

No existe todavia un catalogo operativo de skills de desarrollo, proyecto y negocio. Este documento crea ese catalogo como contrato declarativo. No registra nuevas skills ejecutables y no modifica runtime MCP.

## Leyes de los skills SmartPyme

1. No fact sin evidencia.
2. No hallazgo sin diferencia cuantificada.
3. No accion sin confirmacion.
4. Hermes no decide.
5. SmartPyme gobierna estados.
6. Toda incertidumbre bloquea o genera clarification.
7. Todo output debe ser validable.
8. Todo avance del repo debe tener veredicto, archivos tocados, validacion y siguiente paso unico.

## Relacion con modelos existentes

| modelo | ubicacion | uso actual | relacion con este catalogo |
|---|---|---|---|
| `SkillSpec` | `app/factory/skills/models.py` | Modelo runtime minimo para ejecutar skills builtin. | No se duplica ni se reemplaza. |
| `SkillContract` | `app/contracts/skill_contract.py` | Contrato declarativo ampliado. | Sirve para planificar antes de registrar runtime. |
| `Job.skill_id` | `app/factory/orchestrator/models.py` | Identifica la skill que ejecutara un job. | Debe referenciar skills registradas solo cuando esten implementadas. |

## Contrato minimo

Cada skill del catalogo debe declarar:

- `skill_id`
- `family`
- `purpose`
- `input_schema`
- `output_schema`
- `required_evidence`
- `allowed_tools`
- `forbidden_actions`
- `blocking_conditions`
- `acceptance_criteria`
- `implementation_status`
- `source_files`
- `next_action`

## A. Skills de desarrollo

### skill_audit_repo_state

| campo | valor |
|---|---|
| family | development |
| purpose | Auditar estado del repo antes de tocar archivos. |
| input_schema | `{ "type": "object", "required": ["scope"], "properties": { "scope": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["verdict", "files_seen", "risks"], "properties": { "verdict": { "type": "string" }, "files_seen": { "type": "array", "items": { "type": "string" } }, "risks": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | `git status`, `rg --files`, documentos canonicos |
| allowed_tools | lectura de archivos, busqueda local |
| forbidden_actions | modificar logica, tocar Hermes config |
| blocking_conditions | acceso denegado a rutas criticas, estado no evidenciado |
| acceptance_criteria | veredicto, inventario, riesgos reales |
| implementation_status | partial |
| source_files | `docs/SMARTPYME_OS_ACTUAL.md`, `docs/ARCHIVO_LEGACY.md` |
| next_action | Formalizar como helper documental antes de automatizar. |

### skill_apply_minimal_patch

| campo | valor |
|---|---|
| family | development |
| purpose | Aplicar cambios minimos con alcance declarado. |
| input_schema | `{ "type": "object", "required": ["objective", "allowed_files"], "properties": { "objective": { "type": "string" }, "allowed_files": { "type": "array", "items": { "type": "string" } } } }` |
| output_schema | `{ "type": "object", "required": ["files_touched", "summary"], "properties": { "files_touched": { "type": "array", "items": { "type": "string" } }, "summary": { "type": "string" } } }` |
| required_evidence | alcance aprobado, diff local |
| allowed_tools | `apply_patch`, checks locales |
| forbidden_actions | redisenar, borrar sin aprobacion, tocar archivos fuera de alcance |
| blocking_conditions | cambios sucios conflictivos, alcance ambiguo |
| acceptance_criteria | patch minimo, sin cambios colaterales |
| implementation_status | conceptual |
| source_files | no runtime |
| next_action | Mantener como regla de trabajo, no registrar aun. |

### skill_validate_e2e_bridge

| campo | valor |
|---|---|
| family | development |
| purpose | Validar el bridge MCP completo con entorno descartable. |
| input_schema | `{ "type": "object", "required": ["destructive_allowed"], "properties": { "destructive_allowed": { "type": "boolean" } } }` |
| output_schema | `{ "type": "object", "required": ["status", "tools_validated"], "properties": { "status": { "type": "string" }, "tools_validated": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | salida de `tests/e2e/validate_bridge_e2e.py` |
| allowed_tools | tests locales, DB temporal |
| forbidden_actions | ejecutar contra DB real sin confirmacion |
| blocking_conditions | `destructive_allowed=false`, falta `hermes-agent`, falta dependencia |
| acceptance_criteria | tools MCP reales validadas o bloqueo explicado |
| implementation_status | partial |
| source_files | `tests/e2e/validate_bridge_e2e.py` |
| next_action | Hacerlo seguro con DB temporales antes de automatizar. |

### skill_update_docs_after_patch

| campo | valor |
|---|---|
| family | development |
| purpose | Actualizar docs canonicos despues de cambios reales. |
| input_schema | `{ "type": "object", "required": ["changed_files"], "properties": { "changed_files": { "type": "array", "items": { "type": "string" } } } }` |
| output_schema | `{ "type": "object", "required": ["docs_updated", "notes"], "properties": { "docs_updated": { "type": "array", "items": { "type": "string" } }, "notes": { "type": "string" } } }` |
| required_evidence | diff, docs canonicos |
| allowed_tools | editar docs |
| forbidden_actions | documentar estado no probado |
| blocking_conditions | no hay evidencia de cambio |
| acceptance_criteria | docs reflejan runtime real |
| implementation_status | partial |
| source_files | `docs/SMARTPYME_OS_ACTUAL.md`, `docs/HERMES_MCP_RUNTIME.md`, `docs/ROADMAP_IMPLEMENTACION.md` |
| next_action | Usar manualmente hasta cerrar contratos. |

### skill_detect_legacy_conflicts

| campo | valor |
|---|---|
| family | development |
| purpose | Detectar documentos o skeletons que contradicen runtime real. |
| input_schema | `{ "type": "object", "required": ["paths"], "properties": { "paths": { "type": "array", "items": { "type": "string" } } } }` |
| output_schema | `{ "type": "object", "required": ["conflicts"], "properties": { "conflicts": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | `docs/ARCHIVO_LEGACY.md`, busquedas por naming viejo |
| allowed_tools | lectura y busqueda |
| forbidden_actions | borrar legacy sin aprobacion |
| blocking_conditions | no se puede leer ruta |
| acceptance_criteria | conflictos clasificados por accion recomendada |
| implementation_status | partial |
| source_files | `docs/ARCHIVO_LEGACY.md`, `docs/archive/FUENTES_DEPRECABLES.md` |
| next_action | Mantenerlo como checklist de limpieza. |

## B. Skills de proyecto

### skill_generate_operational_plan_contract

| campo | valor |
|---|---|
| family | project |
| purpose | Generar el contrato de plan operativo antes de crear jobs. |
| input_schema | `{ "type": "object", "required": ["owner_request", "scope"], "properties": { "owner_request": { "type": "string" }, "scope": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["plan_id", "steps", "acceptance_criteria"], "properties": { "plan_id": { "type": "string" }, "steps": { "type": "array", "items": { "type": "object" } }, "acceptance_criteria": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | roadmap, docs canonicos, alcance del owner |
| allowed_tools | documentacion, contratos locales |
| forbidden_actions | crear job, ejecutar skills de negocio |
| blocking_conditions | objetivo ambiguo, falta criterio de aceptacion |
| acceptance_criteria | contrato validable y sin accion runtime |
| implementation_status | partial |
| source_files | `docs/ROADMAP_IMPLEMENTACION.md`, `app/contracts/operational_plan_contract.py` |
| next_action | Endurecer validaciones y persistencia del plan si el schema de jobs evoluciona. |

### skill_create_job_from_plan

| campo | valor |
|---|---|
| family | project |
| purpose | Crear un job desde un OperationalPlanContract aprobado. |
| input_schema | `{ "type": "object", "required": ["plan_id", "approved_by"], "properties": { "plan_id": { "type": "string" }, "approved_by": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["job_id", "status"], "properties": { "job_id": { "type": "string" }, "status": { "type": "string" } } }` |
| required_evidence | plan aprobado, skill_id valido |
| allowed_tools | futura tool MCP `create_job` |
| forbidden_actions | crear job sin plan, escribir SQLite directo desde Hermes |
| blocking_conditions | plan no aprobado, skill no registrada, payload invalido |
| acceptance_criteria | job creado en estado inicial y consultable |
| implementation_status | partial |
| source_files | `mcp_smartpyme_bridge.py`, `app/contracts/operational_plan_contract.py`, `app/factory/orchestrator/models.py`, `app/factory/orchestrator/persistence.py` |
| next_action | Usar como base para el siguiente contrato operativo sin registrar skills runtime. |

### skill_map_operational_vectors

| campo | valor |
|---|---|
| family | project |
| purpose | Mapear vectores operativos del negocio a capas SmartPyme. |
| input_schema | `{ "type": "object", "required": ["business_context"], "properties": { "business_context": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["vectors"], "properties": { "vectors": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | documentos del negocio, roadmap |
| allowed_tools | lectura documental, EvidenceStore |
| forbidden_actions | generar hallazgos sin reconciliation |
| blocking_conditions | sin evidencia documental |
| acceptance_criteria | cada vector tiene fuente, entidad y capa destino |
| implementation_status | conceptual |
| source_files | no evidenciado |
| next_action | Definir despues de OperationalPlanContract. |

### skill_define_acceptance_criteria

| campo | valor |
|---|---|
| family | project |
| purpose | Convertir un objetivo en criterios de aceptacion verificables. |
| input_schema | `{ "type": "object", "required": ["objective"], "properties": { "objective": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["criteria"], "properties": { "criteria": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | objetivo, estado real, limites |
| allowed_tools | docs, tests |
| forbidden_actions | aceptar criterios no medibles |
| blocking_conditions | objetivo sin alcance |
| acceptance_criteria | criterios observables y testeables |
| implementation_status | conceptual |
| source_files | `docs/ROADMAP_IMPLEMENTACION.md` |
| next_action | Incorporar al plan contract. |

### skill_trace_roadmap_step

| campo | valor |
|---|---|
| family | project |
| purpose | Trazar cada avance contra el roadmap congelado. |
| input_schema | `{ "type": "object", "required": ["step"], "properties": { "step": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["roadmap_status", "next_step"], "properties": { "roadmap_status": { "type": "string" }, "next_step": { "type": "string" } } }` |
| required_evidence | `docs/ROADMAP_IMPLEMENTACION.md` |
| allowed_tools | lectura de docs |
| forbidden_actions | saltar capas anteriores |
| blocking_conditions | paso no esta en roadmap |
| acceptance_criteria | siguiente paso unico |
| implementation_status | partial |
| source_files | `docs/ROADMAP_IMPLEMENTACION.md` |
| next_action | Usar como gate antes de nuevos cambios. |

## C. Skills de negocio

### skill_ingest_document

| campo | valor |
|---|---|
| family | business |
| purpose | Ingestar un documento local y generar evidencia trazable. |
| input_schema | `{ "type": "object", "required": ["file_path"], "properties": { "file_path": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["status", "evidence_ids"], "properties": { "status": { "type": "string" }, "evidence_ids": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | archivo local existente |
| allowed_tools | `mcp_smartpyme_ingest_document` |
| forbidden_actions | inventar evidencia |
| blocking_conditions | archivo inexistente, error de parser |
| acceptance_criteria | evidencia recuperable por ID |
| implementation_status | implemented |
| source_files | `mcp_smartpyme_bridge.py`, `services/document_ingestion_service.py` |
| next_action | Mantener como tool MCP real. |

### skill_register_raw_document

| campo | valor |
|---|---|
| family | business |
| purpose | Registrar archivo original con hash SHA-256, job_id y plan_id antes del parseo. |
| input_schema | `{ "type": "object", "required": ["file_path"], "properties": { "file_path": { "type": "string" }, "job_id": { "type": "string" }, "plan_id": { "type": "string" }, "source_id": { "type": "string" }, "metadata": { "type": "object" } } }` |
| output_schema | `{ "type": "object", "required": ["raw_document_id", "file_hash_sha256"], "properties": { "raw_document_id": { "type": "string" }, "file_hash_sha256": { "type": "string" } } }` |
| required_evidence | archivo local existente |
| allowed_tools | `app/repositories/raw_document_registry.py` |
| forbidden_actions | sobrescribir documento original |
| blocking_conditions | archivo inexistente |
| acceptance_criteria | registro idempotente y trazable |
| implementation_status | implemented |
| source_files | `app/contracts/evidence_contract.py`, `app/repositories/raw_document_registry.py` |
| next_action | Mantener integracion minima con `ingest_document`; no crear tool MCP nueva todavia. |

### skill_ingest_document_batch

| campo | valor |
|---|---|
| family | business |
| purpose | Ingestar lote controlado de documentos con errores trazables. |
| input_schema | `{ "type": "object", "required": ["file_paths"], "properties": { "file_paths": { "type": "array", "items": { "type": "string" } } } }` |
| output_schema | `{ "type": "object", "required": ["ingested", "errors"], "properties": { "ingested": { "type": "array", "items": { "type": "string" } }, "errors": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | lista de archivos locales |
| allowed_tools | `DocumentIngestionService` futuro batch |
| forbidden_actions | abortar todo el lote por un archivo fallido sin reporte |
| blocking_conditions | lote vacio |
| acceptance_criteria | resumen con ingestas y errores |
| implementation_status | pending |
| source_files | `services/document_ingestion_service.py` |
| next_action | Extender ingestion sin romper `ingest_document`. |

### skill_chunk_document

| campo | valor |
|---|---|
| family | business |
| purpose | Crear EvidenceChunks trazables desde DocumentRecord. |
| input_schema | `{ "type": "object", "required": ["document_id"], "properties": { "document_id": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["evidence_ids"], "properties": { "evidence_ids": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | DocumentRecord parseado |
| allowed_tools | `extraction.chunker.split_document` |
| forbidden_actions | chunk sin pagina ni source |
| blocking_conditions | texto vacio |
| acceptance_criteria | cada chunk tiene evidence_id, pagina y metadata |
| implementation_status | partial |
| source_files | `extraction/chunker.py`, `models/document_models.py` |
| next_action | Mapear `DocumentChunk` a `EvidenceChunk`. |

### skill_retrieve_evidence

| campo | valor |
|---|---|
| family | business |
| purpose | Recuperar evidencia por id, texto o metadata. |
| input_schema | `{ "type": "object", "required": ["query"], "properties": { "query": { "type": "string" }, "job_id": { "type": "string" }, "plan_id": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["results"], "properties": { "results": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | EvidenceChunks existentes |
| allowed_tools | `mcp_smartpyme_get_evidence`, retrieval local futuro |
| forbidden_actions | responder facts sin evidencia |
| blocking_conditions | evidencia insuficiente |
| acceptance_criteria | resultados con cita validable |
| implementation_status | partial |
| source_files | `mcp_smartpyme_bridge.py`, `services/retrieval_service.py` |
| next_action | Crear EvidenceRepository local. |

### skill_extract_fact_candidates

| campo | valor |
|---|---|
| family | business |
| purpose | Extraer candidatos de facts con schema validable desde evidencia. |
| input_schema | `{ "type": "object", "required": ["evidence_ids", "schema_name"], "properties": { "evidence_ids": { "type": "array", "items": { "type": "string" } }, "schema_name": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["fact_candidates"], "properties": { "fact_candidates": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | evidence_ids recuperables |
| allowed_tools | extractor futuro |
| forbidden_actions | fact sin schema o sin evidence_id |
| blocking_conditions | schema ausente, evidencia insuficiente |
| acceptance_criteria | cada fact candidate valida contra schema |
| implementation_status | pending |
| source_files | `app/contracts/evidence_contract.py` |
| next_action | Definir primer schema de fact. |

### skill_validate_evidence_trace

| campo | valor |
|---|---|
| family | business |
| purpose | Validar que facts, rows, mensajes y hallazgos tengan evidencia recuperable. |
| input_schema | `{ "type": "object", "required": ["items"], "properties": { "items": { "type": "array", "items": { "type": "object" } } } }` |
| output_schema | `{ "type": "object", "required": ["valid", "errors"], "properties": { "valid": { "type": "boolean" }, "errors": { "type": "array", "items": { "type": "string" } } } }` |
| required_evidence | evidence_id por item |
| allowed_tools | EvidenceRepository futuro |
| forbidden_actions | aceptar citas no recuperables |
| blocking_conditions | evidence_id faltante o inexistente |
| acceptance_criteria | todo item trazable o bloqueo |
| implementation_status | pending |
| source_files | `docs/EVIDENCE_CONTRACT.md` |
| next_action | Implementar al crear ExtractedFactCandidate. |

### skill_generate_canonical_rows

| campo | valor |
|---|---|
| family | business |
| purpose | Convertir fact candidates validados en canonical row candidates. |
| input_schema | `{ "type": "object", "required": ["fact_candidates"], "properties": { "fact_candidates": { "type": "array", "items": { "type": "object" } } } }` |
| output_schema | `{ "type": "object", "required": ["canonical_rows"], "properties": { "canonical_rows": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | fact candidates validados |
| allowed_tools | normalizador futuro |
| forbidden_actions | row sin fact_candidate_id o evidence_id |
| blocking_conditions | fact candidate invalido |
| acceptance_criteria | rows con schema y trazabilidad |
| implementation_status | pending |
| source_files | `app/contracts/evidence_contract.py` |
| next_action | Implementar despues del primer schema de fact. |

### skill_extract_business_facts

| campo | valor |
|---|---|
| family | business |
| purpose | Extraer hechos de negocio desde evidencia documental. |
| input_schema | `{ "type": "object", "required": ["evidence_ids"], "properties": { "evidence_ids": { "type": "array", "items": { "type": "string" } } } }` |
| output_schema | `{ "type": "object", "required": ["facts"], "properties": { "facts": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | `evidence_ids` validos |
| allowed_tools | `mcp_smartpyme_get_evidence` |
| forbidden_actions | inferir sin evidencia |
| blocking_conditions | evidencia ausente o insuficiente |
| acceptance_criteria | cada fact incluye fuente y confianza |
| implementation_status | pending |
| source_files | `services/document_query_service.py` |
| next_action | Definir contrato de fact antes de normalizacion. |

### skill_normalize_canonical_rows

| campo | valor |
|---|---|
| family | business |
| purpose | Convertir hechos en filas canonicas comparables. |
| input_schema | `{ "type": "object", "required": ["facts"], "properties": { "facts": { "type": "array", "items": { "type": "object" } } } }` |
| output_schema | `{ "type": "object", "required": ["canonical_rows"], "properties": { "canonical_rows": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | facts con fuentes |
| allowed_tools | servicios de normalizacion futuros |
| forbidden_actions | mezclar normalizacion con reconciliacion |
| blocking_conditions | campos obligatorios faltantes |
| acceptance_criteria | filas validables y trazables |
| implementation_status | pending |
| source_files | no evidenciado |
| next_action | Implementar despues de ingesta batch. |

### skill_resolve_entities

| campo | valor |
|---|---|
| family | business |
| purpose | Resolver identidad de entidades antes de comparar. |
| input_schema | `{ "type": "object", "required": ["canonical_rows"], "properties": { "canonical_rows": { "type": "array", "items": { "type": "object" } } } }` |
| output_schema | `{ "type": "object", "required": ["resolved_entities"], "properties": { "resolved_entities": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | canonical rows |
| allowed_tools | entity resolution futura, clarifications si hay duda |
| forbidden_actions | comparar entidades no resueltas |
| blocking_conditions | identidad ambigua |
| acceptance_criteria | entity_id estable o clarification creada |
| implementation_status | pending |
| source_files | no evidenciado |
| next_action | Definir despues de canonical rows. |

### skill_request_clarification

| campo | valor |
|---|---|
| family | business |
| purpose | Crear o gestionar una clarification bloqueante ante incertidumbre. |
| input_schema | `{ "type": "object", "required": ["description"], "properties": { "description": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["clarification_id", "status"], "properties": { "clarification_id": { "type": "string" }, "status": { "type": "string" } } }` |
| required_evidence | incertidumbre o falta de dato |
| allowed_tools | `mcp_smartpyme_save_clarification`, `mcp_smartpyme_list_pending_validations`, `mcp_smartpyme_resolve_clarification` |
| forbidden_actions | avanzar con incertidumbre activa |
| blocking_conditions | descripcion vacia, resolucion vacia |
| acceptance_criteria | clarification persistida o resuelta en SQLite |
| implementation_status | implemented |
| source_files | `mcp_smartpyme_bridge.py`, `app/core/clarification/persistence.py` |
| next_action | Mantener como tool MCP real. |

### skill_reconcile_vectors

| campo | valor |
|---|---|
| family | business |
| purpose | Comparar vectores o registros y cuantificar diferencias. |
| input_schema | `{ "type": "object", "required": ["source_a", "source_b"], "properties": { "source_a": { "type": "array", "items": { "type": "object" } }, "source_b": { "type": "array", "items": { "type": "object" } } } }` |
| output_schema | `{ "type": "object", "required": ["differences"], "properties": { "differences": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | entidades resueltas, filas canonicas |
| allowed_tools | servicios de reconciliation existentes |
| forbidden_actions | exponer por MCP antes de normalizacion/entity resolution |
| blocking_conditions | entidades no validadas, monto incierto |
| acceptance_criteria | diferencias cuantificadas o clarification |
| implementation_status | partial |
| source_files | `app/core/reconciliation/service.py`, `app/core/reconciliation/models.py` |
| next_action | Cerrar contrato operativo antes de tool MCP. |

### skill_generate_hallazgos

| campo | valor |
|---|---|
| family | business |
| purpose | Convertir diferencias cuantificadas en hallazgos trazables. |
| input_schema | `{ "type": "object", "required": ["differences"], "properties": { "differences": { "type": "array", "items": { "type": "object" } } } }` |
| output_schema | `{ "type": "object", "required": ["hallazgos"], "properties": { "hallazgos": { "type": "array", "items": { "type": "object" } } } }` |
| required_evidence | diferencias cuantificadas |
| allowed_tools | `HallazgoEngine` |
| forbidden_actions | hallazgo sin delta/evidencia |
| blocking_conditions | diferencia no cuantificada |
| acceptance_criteria | dedupe_key, evidencia y severidad |
| implementation_status | partial |
| source_files | `app/core/hallazgos/service.py`, `app/core/hallazgos/models.py` |
| next_action | Definir persistencia/ciclo de vida antes de MCP. |

### skill_prepare_owner_message

| campo | valor |
|---|---|
| family | business |
| purpose | Preparar mensaje al dueño con evidencia, impacto y accion sugerida. |
| input_schema | `{ "type": "object", "required": ["hallazgos"], "properties": { "hallazgos": { "type": "array", "items": { "type": "object" } } } }` |
| output_schema | `{ "type": "object", "required": ["message", "requires_confirmation"], "properties": { "message": { "type": "string" }, "requires_confirmation": { "type": "boolean" } } }` |
| required_evidence | hallazgos trazables |
| allowed_tools | generacion de texto con citas |
| forbidden_actions | ocultar incertidumbre, pedir accion sin evidencia |
| blocking_conditions | hallazgo no trazable |
| acceptance_criteria | mensaje con que pasa, con quien, cuanto, que hacer |
| implementation_status | conceptual |
| source_files | `docs/archive/smarttimes_full_architecture.md` como antecedente historico |
| next_action | Diseñar despues de hallazgos. |

### skill_confirm_and_execute_action

| campo | valor |
|---|---|
| family | business |
| purpose | Ejecutar accion confirmada por el dueño. |
| input_schema | `{ "type": "object", "required": ["action_id", "confirmed_by"], "properties": { "action_id": { "type": "string" }, "confirmed_by": { "type": "string" } } }` |
| output_schema | `{ "type": "object", "required": ["status", "audit_ref"], "properties": { "status": { "type": "string" }, "audit_ref": { "type": "string" } } }` |
| required_evidence | confirmacion humana, hallazgo validado |
| allowed_tools | action engine futuro |
| forbidden_actions | accion sin confirmacion, accion con incertidumbre |
| blocking_conditions | falta confirmacion, hallazgo pendiente |
| acceptance_criteria | accion auditada y reversible cuando aplique |
| implementation_status | conceptual |
| source_files | no evidenciado |
| next_action | Posponer hasta cerrar hallazgos. |

## Skills minimos antes de OperationalPlanContract + create_job

1. `skill_generate_operational_plan_contract`
2. `skill_define_acceptance_criteria`
3. `skill_trace_roadmap_step`
4. `skill_audit_repo_state`
5. `skill_validate_e2e_bridge`

## Decisiones de registro

No se agregan estas skills a `SkillRegistry` todavia.

Motivo:

- el registry actual ejecuta `SkillSpec` con `executor_ref`;
- la mayoria del catalogo es contrato operativo pendiente;
- registrar skills sin executor real generaria ruido o falsos positivos;
- `create_job` debe depender de skills implementadas o de un estado explicitamente bloqueado.

El siguiente paso tecnico es implementar `OperationalPlanContract` y luego exponer `create_job` via MCP, usando este catalogo como frontera.
