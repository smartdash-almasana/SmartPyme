# MCP Tools Contract — SmartPyme Bridge

## Transporte canónico

SmartPyme Bridge opera por `stdio`.

Hermes Gateway lanza el bridge como subproceso local:

```yaml
mcp:
  servers:
    smartpyme:
      transport: "stdio"
      command: "/home/neoalmasana/smartpyme-factory/repos/SmartPyme/.venv/bin/python"
      args:
        - "/home/neoalmasana/smartpyme-factory/repos/SmartPyme/mcp_smartpyme_bridge.py"
```

No existe endpoint HTTP `localhost:8080/mcp` para el bridge vigente.

## Dirección de integración BEM

La integración BEM por MCP debe entenderse como una capacidad expuesta por el bridge SmartPyme para que el sistema invoque workflows BEM desde una frontera controlada.

Flujo objetivo:

```text
SmartPyme / Gateway autorizado
-> SmartPyme MCP Bridge
-> bem_submit_workflow
-> BemSubmitService
-> BemClient
-> BEM workflow
-> BemRunRepository
-> BemCuratedEvidenceAdapter.build_curated_evidence_from_bem_response(...)
-> CuratedEvidenceRepositoryBackend
```

La herramienta MCP no reemplaza el contrato soberano de evidencia curada. Cubre la salida controlada SmartPyme -> BEM y la promoción automática a evidencia curada cuando BEM responde con `outputs[0].transformedContent`.

Estructura del `response_payload` real de BEM:

```json
{
  "callReferenceID": "...",
  "callID": "...",
  "avgConfidence": 0.91,
  "inputType": "excel",
  "outputs": [
    {
      "transformedContent": {
        "producto": "Mouse Gamer RGB",
        "precio_venta": 10,
        "costo_unitario": 80,
        "cantidad": 5,
        "source_name": "ventas_demo.xlsx",
        "source_type": "excel"
      }
    }
  ]
}
```

Mapeo `response_payload` → `CuratedEvidenceRecord`:

- `evidence_id`: `callReferenceID` → `callID` → `bem-run-{run_id}` → fail-closed
- `kind`: inferido desde `inputType` o `source_type`
- `payload.data`: `precio_venta`, `costo_unitario`, `cantidad`, `producto`
- `source_metadata`: `source_name` / `source_type` desde `transformedContent`
- `confidence`: desde `avgConfidence` si existe
- `tenant_id`: preservado desde contexto del run

## Reglas

- Hermes o gateway autorizado invoca tools MCP; no importa core Python directamente.
- El bridge no decide flujo de factoría.
- El bridge no saltea validaciones humanas.
- Toda respuesta debe indicar si viene de backend real o de fallback explícito.
- Toda tool que invoque servicios externos debe operar fail-closed.
- Ninguna tool debe imprimir secretos, API keys o tokens.
- Los payloads deben ser JSON serializables.
- Las respuestas deben preservar `tenant_id`, `workflow_id`, `run_id` cuando correspondan.

## Tools esperadas

### Operación SmartPyme / factoría

- `create_job`
- `get_job_status`
- `list_pending_validations`
- `resolve_clarification`
- `save_clarification`
- `get_evidence`
- `ingest_document`
- `bem_submit_workflow`

## BEM Submit (SmartPyme -> MCP -> BEM)

La integración de submit a BEM queda expuesta por la tool MCP:

- `bem_submit_workflow(tenant_id, workflow_id, payload, db_path?)`

Contrato operativo:

- Persistencia de run en SQLite (`data/bem_runs.db` por defecto o `db_path`).
- Promoción automática a `CuratedEvidenceRecord` en `data/curated_evidence.db` (o `SMARTPYME_CURATED_EVIDENCE_DB_PATH`) si el `response_payload` contiene `outputs[0].transformedContent`.
- Estado `COMPLETED` cuando BEM responde OK y curated evidence fue persistido.
- Estado `REJECTED` con `error_type=BEM_UPSTREAM_ERROR` ante falla de BEM.
- Estado `REJECTED` con `error_type=INTERNAL_ERROR` si el adapter falla (response_payload sin estructura BEM esperada).
- Sin exposición de secretos.

Implementación mínima asociada:

- `app/services/bem_submit_port.py`
- `app/services/bem_mcp_submit_adapter.py`
- `app/services/bem_submit_service.py`
- `app/services/bem_curated_evidence_adapter.py` — método `build_curated_evidence_from_bem_response`
- `app/repositories/curated_evidence_repository.py`

Compatibilidad:

- Se preserva submit HTTP directo vía `BemClient`.
- SmartPyme puede operar con adapter MCP tenant-aware o cliente HTTP directo.
- Si `curated_evidence_repository` no se inyecta en `BemSubmitService`, el comportamiento anterior queda intacto.

### BEM

- `bem_submit_workflow`

Contrato esperado de `bem_submit_workflow`:

```json
{
  "tenant_id": "acme-demo",
  "workflow_id": "smartpyme-venta-bajo-costo",
  "payload": {
    "producto": "Mouse Gamer RGB",
    "precio_venta": 10,
    "costo_unitario": 80,
    "cantidad": 5,
    "source_name": "ventas_demo.xlsx",
    "source_type": "excel"
  },
  "db_path": "data/bem_runs.db"
}
```

`db_path` es opcional. Si no se informa, debe usarse la ruta por defecto o `SMARTPYME_BEM_RUNS_DB_PATH`.

Respuesta esperada en éxito:

```json
{
  "status": "COMPLETED",
  "run_id": "...",
  "tenant_id": "acme-demo",
  "workflow_id": "smartpyme-venta-bajo-costo",
  "response_payload": {}
}
```

Respuesta esperada en rechazo:

```json
{
  "status": "REJECTED",
  "tenant_id": "acme-demo",
  "workflow_id": "smartpyme-venta-bajo-costo",
  "error_code": "BEM_UPSTREAM_ERROR"
}
```

Errores permitidos:

- `BEM_UPSTREAM_ERROR`
- `INTERNAL_ERROR`

## Persistencia BEM

La salida inmediata de BEM se registra en:

```text
BemRunRepository
```

DB local por defecto:

```text
data/bem_runs.db
```

Configuración alternativa:

```text
SMARTPYME_BEM_RUNS_DB_PATH
```

Este registro conserva el run y el `response_payload` de BEM.

Inmediatamente después, si el `response_payload` contiene `outputs[0].transformedContent`, se promueve automáticamente a evidencia curada:

```text
CuratedEvidenceRepositoryBackend
```

DB local por defecto:

```text
data/curated_evidence.db
```

Configuración alternativa:

```text
SMARTPYME_CURATED_EVIDENCE_DB_PATH
```

## Validación

```bash
grep -n "mcp.run" mcp_smartpyme_bridge.py
grep -n "bem_submit_workflow" mcp_smartpyme_bridge.py
pytest tests/api/test_bem_submit_router.py tests/test_mcp_smartpyme_bridge.py tests/services/test_bem_submit_service_curated_evidence.py tests/services/test_bem_curated_evidence_adapter.py -q --tb=short
```

## Criterio de alineación

La documentación BEM debe permanecer consistente con:

- `docs/adr/ADR-004-bem-curated-evidence-boundary.md`
- `docs/operational/BEM_REAL_SUBMIT.md`
- `docs/operational/BEM_DIAGNOSTIC_SMOKE.md`

Regla de frontera vigente:

```text
Documento crudo -> BEM
Evidencia curada -> SmartPyme
```
