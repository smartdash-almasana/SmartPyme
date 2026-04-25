# Hermes MCP runtime

## Config real de Hermes

Hermes carga SmartPyme desde:

`C:\Users\PC\.hermes\config.yaml`

Configuracion observada:

```yaml
mcp_servers:
  smartpyme:
    enabled: true
    command: "C:/Python314/python.exe"
    args:
      - "E:/BuenosPasos/smartbridge/SmartPyme/mcp_smartpyme_bridge.py"
```

Esta configuracion no debe modificarse desde SmartPyme sin una decision explicita de operacion.

## Bridge MCP

El bridge activo es:

`mcp_smartpyme_bridge.py`

Corre como servidor MCP por stdio:

```python
mcp = FastMCP("SmartPyme-Bridge")
...
mcp.run()
```

Hermes no importa el core de SmartPyme como libreria de aplicacion. Hermes invoca tools MCP registradas por el bridge.

## Tools registradas

| tool MCP | funcion | persistencia / servicio |
|---|---|---|
| `create_job` | Crea un job desde un OperationalPlanContract minimo | SQLite `data/jobs.db` |
| `get_job_status` | Consulta estado de un job | SQLite `data/jobs.db` |
| `list_pending_validations` | Lista clarificaciones pendientes | SQLite `data/clarifications.db` |
| `resolve_clarification` | Resuelve una clarificacion | SQLite `data/clarifications.db` |
| `save_clarification` | Crea una clarificacion manual | SQLite `data/clarifications.db` |
| `get_evidence` | Recupera un chunk de evidencia | `evidence_store/document_chunks/chunks.jsonl` |
| `ingest_document` | Ingesta un archivo local | `DocumentIngestionService` + EvidenceStore |

## Comando de validacion

Validacion E2E del bridge:

```powershell
python tests/e2e/validate_bridge_e2e.py
```

El script importa `handle_function_call` desde `hermes-agent` y llama las tools como `mcp_smartpyme_<tool>`.

Advertencia: el script borra bases y evidence store de prueba al limpiar. No ejecutarlo contra datos que deban conservarse.

## Limites de Hermes

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
- gobernar normalizacion, entity resolution, reconciliacion o action engine si no existe tool MCP activa para eso;
- tratar skeletons, blueprints o documentos historicos como runtime real.

## Lectura correcta del runtime

La frase correcta ya no es "bridge stub". El bridge tiene tools reales.

Matiz importante: algunas respuestas contemplan ausencia de datos, por ejemplo `get_evidence` devuelve `stub_explicit` si falta el evidence store. Eso no convierte al bridge completo en stub; indica una rama explicita de error/ausencia.
