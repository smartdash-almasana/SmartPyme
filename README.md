# SmartPyme

SmartPyme es el sistema de verdad operativo. Hermes Agent es el operador conversacional. MCP es el contrato entre Hermes y SmartPyme.

## Estado actual

- Hermes carga SmartPyme desde `C:\Users\PC\.hermes\config.yaml`.
- El bridge MCP real vive en `mcp_smartpyme_bridge.py`.
- El bridge expone tools MCP reales para jobs, clarificaciones, ingesta documental y evidencia.
- Jobs usa SQLite local en `data/jobs.db`.
- Clarifications usa SQLite local en `data/clarifications.db`.
- EvidenceStore usa archivos locales bajo `evidence_store/`.

## Bridge MCP

Tools reales actualmente documentadas:

- `mcp_smartpyme_create_job`
- `mcp_smartpyme_get_job_status`
- `mcp_smartpyme_save_clarification`
- `mcp_smartpyme_list_pending_validations`
- `mcp_smartpyme_resolve_clarification`
- `mcp_smartpyme_ingest_document`
- `mcp_smartpyme_get_evidence`

## Validacion E2E

Comando:

```powershell
python tests/e2e/validate_bridge_e2e.py
```

Advertencia: este E2E puede limpiar `jobs.db`, `clarifications.db` y `evidence_store` locales. Ejecutarlo solo con datos descartables o entorno preparado.

## Documentacion canonica

- `docs/architecture/SMARTPYME_OBJECTIVE_MODEL.md` (Mapa Rector)
- `docs/architecture/PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md` (Modelos operativos, síntomas y casos PyME)
- `docs/architecture/PYME_SYMPTOM_PATHOLOGY_ATLAS.md` (Atlas clínico-operativo de síntomas y patologías PyME)
- `docs/architecture/HYPOTHETICO_DEDUCTIVE_METHOD.md` (Método hipotético-deductivo aplicado a PyMEs)
- `docs/architecture/CONVERSATIONAL_METHODS.md` (Métodos conversacionales e investigativos)
- `docs/architecture/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` (Diseño del catálogo síntoma-patología-skill)
- Motor de abastecimiento externo de conocimiento
   apuntando a:
   docs/architecture/EXTERNAL_KNOWLEDGE_INTAKE_ENGINE.md
- [Principios aprovechables de Palantir para SmartPyme](docs/architecture/PALANTIR_PRINCIPLES_FOR_SMARTPYME.md)
- `docs/architecture/SPECIFIC_KNOWLEDGE_TANKS_AND_SOURCE_ENGINE.md` (Tanques específicos y motor de fuentes idóneas)
- `docs/SMARTPYME_OS_ACTUAL.md`
- `docs/HERMES_MCP_RUNTIME.md`
- `docs/ROADMAP_IMPLEMENTACION.md`
- `docs/ARCHIVO_LEGACY.md`

## Utilidades locales

Scripts manuales de seed y validacion no-runtime viven en `scripts/dev/`.

Los documentos de prueba viven en `tests/fixtures/`.
