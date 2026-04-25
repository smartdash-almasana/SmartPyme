# Roadmap de implementacion

Este roadmap congela el orden recomendado despues de la normalizacion documental. No habilita nuevas features por si mismo.

## Cerrado / evidenciado

1. Bridge MCP real entre Hermes y SmartPyme.
2. Config de Hermes apuntando a `mcp_smartpyme_bridge.py`.
3. `get_job_status` leyendo SQLite real.
4. Persistencia minima de jobs en `data/jobs.db`.
5. `orchestrate_job` persistiendo transiciones.
6. Clarifications CRUD minimo en SQLite.
7. `ingest_document` usando `DocumentIngestionService`.
8. `get_evidence` leyendo EvidenceStore JSONL.
9. Validacion E2E del bridge en `tests/e2e/validate_bridge_e2e.py`.
10. RawDocument registry local en SQLite.
11. Hash SHA-256 de archivo original antes de ingesta.
## Siguiente inmediato

1. Limpieza repo sin borrar todavia.
   - Marcar documentos y scripts por categoria.
   - Proponer archivo controlado en `docs/archive/`.
   - Separar runtime MCP de factory/skeletons.
   - Actualizar README para no afirmar que no hay codigo funcional.

2. OperationalPlanContract.
   - Definido como contrato minimo declarativo en `app/contracts/operational_plan_contract.py`.

3. `create_job` via MCP.
   - Tool MCP minima implementada.
   - Persiste job en `CREATED`, `skill_id` y payload del plan.

## Wrapper de Operación Conversacional

4. Implementar `HermesSmartPymeRuntime` wrapper. (Completado)
   - Crear el wrapper siguiendo la estrategia definida en `docs/HERMES_SMARTPYME_RUNTIME_STRATEGY.md`.
   - Utilizar la configuración segura canónica de `AIAgent`.
   - Mapear `job_id` a `session_id`.
   - Exponer una interfaz mínima para iniciar una conversación y recibir el resultado.

## Pendiente medio plazo

4. RAW/RAG local antes de Supabase.
   - RawDocument registry local. Implementado minimo.
   - Hash de archivo original + metadata minima. Implementado minimo.
   - Batch ingestion.
   - EvidenceRepository formal local.
   - Retrieval local por texto/metadata.
   - ExtractedFactCandidate.
   - CanonicalRowCandidate.
   - Repository interfaces.
   - Supabase adapter.

5. Ingesta batch.
   - Extender ingesta de archivo unico a lotes controlados.
   - Mantener trazabilidad de source_id, chunks y errores.

6. Normalizacion / canonical rows.
   - Separar texto/chunks de filas canonicas.
   - Definir contratos de entrada/salida.
   - No mezclar con reconciliation.

7. Entity resolution.
   - Resolver identidades de entidades antes de comparar.
   - Integrar con clarifications cuando haya incertidumbre.

8. Reconciliacion.
   - Llevar el servicio existente a contrato operativo cerrado.
   - Exponer por MCP solo cuando el flujo de datos anterior este definido.

## Pendiente largo plazo

9. Hallazgos.
   - Consolidar termino de negocio "hallazgos".
   - Definir repositorio, severidad, trazabilidad y ciclo de vida.
   - Mantener `findings` solo donde sea nombre tecnico legado.

10. Action engine.
   - Acciones despues de hallazgos validados.
   - No ejecutar acciones sin trazabilidad, autorizacion y estados cerrados.

## RAW/RAG antes de Supabase

Orden congelado:

1. RawDocument registry local. Implementado minimo.
2. Hash + metadata. Implementado minimo.
3. Batch ingestion.
4. EvidenceRepository formal local.
5. Retrieval local por texto/metadata.
6. ExtractedFactCandidate.
7. CanonicalRowCandidate.
8. Repository interfaces.
9. Supabase adapter.

## Regla de orden

No avanzar a una capa si la anterior no tiene:

- contrato minimo;
- persistencia definida si corresponde;
- tests de contrato;
- documentacion operativa;
- criterio de bloqueo ante incertidumbre.
