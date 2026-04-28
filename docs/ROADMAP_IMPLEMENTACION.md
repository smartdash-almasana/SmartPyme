# Roadmap de implementación

Este roadmap congela el orden recomendado después de la normalización documental. No habilita nuevas features por sí mismo.

## Estado de este documento

Reconciliado el 2026-04-28 para alinearse con `docs/factory/FACTORY_CONTRATO_OPERATIVO.md` y `docs/factory/RUNTIME_VIGENTE.md`.

La regla vigente es:

```text
Hermes Gateway externo = runtime conversacional vigente
factory/hermes_control_cli.py = adaptador interno permitido
scripts/hermes_factory_runner.py = LEGACY_DEPRECATED / PROHIBIDO / NO OPERATIVO
scripts/telegram_factory_control.py = LEGACY_DEPRECATED / PROHIBIDO / NO OPERATIVO
```

## Cerrado / evidenciado

1. Bridge MCP real entre Hermes y SmartPyme.
2. Config de Hermes apuntando a `mcp_smartpyme_bridge.py`.
3. `get_job_status` leyendo SQLite real.
4. Persistencia mínima de jobs en `data/jobs.db`.
5. `orchestrate_job` persistiendo transiciones.
6. Clarifications CRUD mínimo en SQLite.
7. `ingest_document` usando `DocumentIngestionService`.
8. `get_evidence` leyendo EvidenceStore JSONL.
9. Validación E2E del bridge en `tests/e2e/validate_bridge_e2e.py`.
10. RawDocument registry local en SQLite.
11. Hash SHA-256 de archivo original antes de ingesta.
12. Runtime conversacional vigente definido: Hermes Gateway externo + adaptador `factory/hermes_control_cli.py`.

## Estado histórico de runners legacy

`factory/hallazgos/*` no es la cola activa de factoría. Permanece como antecedente o dominio pendiente de contrato operativo explícito.

Los runners legacy no son parte del roadmap productivo activo:

```text
scripts/hermes_factory_runner.py
scripts/telegram_factory_control.py
run_sfma_cycle.sh
```

Toda referencia a esos nombres debe interpretarse como histórica, deprecada, prohibida o no operativa.

## Siguiente inmediato

1. Cierre P0 documental/infra.
   - Mantener `docs/factory/RUNTIME_VIGENTE.md` como fuente única de runtime.
   - Asegurar que workflows y services no invoquen runners legacy.
   - Marcar documentos y scripts legacy por categoría.
   - Separar runtime MCP de factoría y skeletons.

2. P1 — Contrato de handoff entre agentes.
   - Hermes Gateway → Codex Builder → Gemini Auditor → ChatGPT Director/Auditor.
   - Definir payloads, ownership de evidencia y estados.

3. P2 — Gobernanza de roles y veredictos.
   - Codex = Builder.
   - Gemini = Auditor técnico.
   - ChatGPT = Director/Auditor externo.
   - Unificar vocabulario de veredictos.

## Wrapper de operación conversacional

El wrapper conversacional no reemplaza Hermes Gateway. Cualquier wrapper o CLI interno debe operar como adaptador controlado, no como runtime autónomo.

## Pendiente medio plazo

4. RAW/RAG local antes de Supabase.
   - RawDocument registry local. Implementado mínimo.
   - Hash de archivo original + metadata mínima. Implementado mínimo.
   - Batch ingestion.
   - EvidenceRepository formal local.
   - Retrieval local por texto/metadata.
   - ExtractedFactCandidate.
   - CanonicalRowCandidate.
   - Repository interfaces.
   - Supabase adapter.

5. Ingesta batch.
   - Extender ingesta de archivo único a lotes controlados.
   - Mantener trazabilidad de source_id, chunks y errores.

6. Normalización / canonical rows.
   - Separar texto/chunks de filas canónicas.
   - Definir contratos de entrada/salida.
   - No mezclar con reconciliation.

7. Entity resolution.
   - Resolver identidades de entidades antes de comparar.
   - Integrar con clarifications cuando haya incertidumbre.

8. Reconciliación.
   - Llevar el servicio existente a contrato operativo cerrado.
   - Exponer por MCP solo cuando el flujo de datos anterior esté definido.

## Pendiente largo plazo

9. Hallazgos.
   - Consolidar término de negocio "hallazgos".
   - Definir repositorio, severidad, trazabilidad y ciclo de vida.
   - Mantener `findings` solo donde sea nombre técnico legado.

10. Action engine.
   - Acciones después de hallazgos validados.
   - No ejecutar acciones sin trazabilidad, autorización y estados cerrados.

## RAW/RAG antes de Supabase

Orden congelado:

1. RawDocument registry local. Implementado mínimo.
2. Hash + metadata. Implementado mínimo.
3. Batch ingestion.
4. EvidenceRepository formal local.
5. Retrieval local por texto/metadata.
6. ExtractedFactCandidate.
7. CanonicalRowCandidate.
8. Repository interfaces.
9. Supabase adapter.

## Regla de orden

No avanzar a una capa si la anterior no tiene:

- contrato mínimo;
- persistencia definida si corresponde;
- tests de contrato;
- documentación operativa;
- criterio de bloqueo ante incertidumbre.

## Historial de Cambios

- 2026-04-28 — Reconciliado por remediación P0 / DOC-001. Se reemplazó la afirmación de runner operativo en `scripts/hermes_factory_runner.py` por runtime vigente Hermes Gateway externo y se marcó el runner legacy como deprecado/prohibido/no operativo.
