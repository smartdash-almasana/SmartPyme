# Hermes MCP runtime

## Estado de este documento

Reconciliado el 2026-04-28 para alinearse con `docs/factory/RUNTIME_VIGENTE.md`.

Este documento describe **solo** el runtime MCP entre Hermes y SmartPyme. No define el runtime conversacional ni la factoría. El runtime conversacional vigente es Hermes Gateway externo.

## Config productiva de Hermes en VM

Hermes productivo carga configuración local desde:

```text
/home/neoalmasana/.hermes/config.yaml
```

El repositorio editable de Hermes Agent en la VM vive en:

```text
/opt/smartpyme-factory/repos/hermes-agent
```

El repositorio SmartPyme vive en:

```text
/opt/smartpyme-factory/repos/SmartPyme
```

## Entorno de desarrollo Windows no productivo

La configuración Windows histórica puede aparecer en máquinas de desarrollo, pero no es fuente de verdad productiva:

```text
C:\Users\PC\.hermes\config.yaml
E:/BuenosPasos/smartbridge/SmartPyme/mcp_smartpyme_bridge.py
```

No usar esas rutas para operar la VM ni para documentar runtime vigente.

## Runtime de factoría

El runtime conversacional vigente de SmartPyme Factory es Hermes Gateway externo + adaptador interno `factory/hermes_control_cli.py`.

Los runners legacy:

```text
scripts/hermes_factory_runner.py
scripts/telegram_factory_control.py
run_sfma_cycle.sh
```

son `LEGACY_DEPRECATED / PROHIBIDO / NO OPERATIVO` para producción. No deben ejecutarse desde systemd, workflows, Gateway ni scripts de operación.

## Bridge MCP

El bridge activo es:

```text
mcp_smartpyme_bridge.py
```

Corre como servidor MCP por stdio:

```python
mcp = FastMCP("SmartPyme-Bridge")
...
mcp.run()
```

Hermes no importa el core de SmartPyme como librería de aplicación. Hermes invoca tools MCP registradas por el bridge.

## Tools registradas

| tool MCP | función | persistencia / servicio |
|---|---|---|
| `create_job` | Crea un job desde un OperationalPlanContract mínimo | SQLite `data/jobs.db` |
| `get_job_status` | Consulta estado de un job | SQLite `data/jobs.db` |
| `list_pending_validations` | Lista clarificaciones pendientes | SQLite `data/clarifications.db` |
| `resolve_clarification` | Resuelve una clarificación | SQLite `data/clarifications.db` |
| `save_clarification` | Crea una clarificación manual | SQLite `data/clarifications.db` |
| `get_evidence` | Recupera un chunk de evidencia | `evidence_store/document_chunks/chunks.jsonl` |
| `ingest_document` | Ingesta un archivo local | `DocumentIngestionService` + EvidenceStore |

## Comando de validación

Validación E2E del bridge:

```powershell
python tests/e2e/validate_bridge_e2e.py
```

El script importa `handle_function_call` desde `hermes-agent` y llama las tools como `mcp_smartpyme_<tool>`.

Advertencia: el script borra bases y evidence store de prueba al limpiar. No ejecutarlo contra datos que deban conservarse.

## Límites de Hermes sobre SmartPyme

Hermes puede:

- conversar con el usuario;
- pedir estado real a SmartPyme por MCP;
- registrar clarificaciones;
- resolver clarificaciones con respuesta humana;
- pedir ingesta de documentos locales;
- pedir evidencia por ID.

Hermes no debe:

- decidir estados de negocio por fuera de SmartPyme;
- escribir directo en SQLite;
- editar `data/jobs.db` o `data/clarifications.db`;
- saltear MCP para modificar verdad operativa;
- inventar jobs, hallazgos, evidencias o estados no devueltos por SmartPyme;
- gobernar normalización, entity resolution, reconciliación o action engine si no existe tool MCP activa para eso;
- tratar skeletons, blueprints, runners legacy o documentos históricos como runtime real.

## Lectura correcta del runtime

La frase correcta ya no es "bridge stub". El bridge tiene tools reales.

Matiz importante: algunas respuestas contemplan ausencia de datos, por ejemplo `get_evidence` devuelve `stub_explicit` si falta el evidence store. Eso no convierte al bridge completo en stub; indica una rama explícita de error/ausencia.

## Historial de Cambios

- 2026-04-28 — Reconciliado por remediación P0 / DOC-002. Se separó MCP runtime de factoría, se cambiaron rutas productivas a Linux VM y se marcó el runner legacy como deprecado/prohibido/no operativo.
