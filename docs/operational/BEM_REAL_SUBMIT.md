# BEM Real Submit — SmartPyme -> BEM

## Objetivo

Validar envío real de payload curado desde SmartPyme hacia BEM.

También validar submit por frontera MCP cuando SmartPyme actúa como cliente de tool MCP.

---

## Precondiciones

- `BEM_API_KEY` real disponible en entorno.
- `BEM_WORKFLOW_ID` real disponible en entorno.
- App SmartPyme levantada si se prueba por HTTP.

Ejemplo para levantar API local:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Prueba por CLI

```bash
python tools/bem_submit_payload.py --workflow-id "$BEM_WORKFLOW_ID" --payload-file docs/operational/fixtures/bem_payload_venta_bajo_costo.json
```

Notas:
- El CLI toma `BEM_API_KEY` desde variable de entorno (o `--api-key` explícito).
- Imprime JSON de respuesta en formato pretty.

---

## Prueba por HTTP

Endpoint:

```text
POST /api/v1/bem/submit
```

Ejemplo `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/bem/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "acme-demo",
    "workflow_id": "'"$BEM_WORKFLOW_ID"'",
    "payload": {
      "tenant_id": "acme-demo",
      "payload": {
        "evidence_id": "ev-demo-venta-bajo-costo-001",
        "kind": "EXCEL",
        "data": {
          "precio_venta": 10,
          "costo_unitario": 80
        },
        "source": {
          "source_name": "ventas.xlsx",
          "source_type": "excel"
        }
      }
    }
  }'
```

---

## Resultado esperado

- `status = COMPLETED` si BEM responde OK.
- run persistido en `data/bem_runs.db`.

Respuesta esperada en éxito:

```json
{
  "tenant_id": "acme-demo",
  "run_id": "...",
  "workflow_id": "...",
  "status": "COMPLETED"
}
```

---

## Prueba por frontera MCP

Tool MCP:

```text
bem_submit_workflow
```

Entradas:

- `tenant_id`
- `workflow_id`
- `payload`
- `db_path` (opcional)

Resultado esperado:

- `status = COMPLETED` si BEM responde OK.
- run persistido por tenant en SQLite de runs.

---

## Errores esperados

- `400` si falta `tenant_id`, `workflow_id` o `payload`.
- `502` si BEM falla.

Respuesta típica de error:

```json
{
  "detail": "..."
}
```

---

## Aclaración

- Esta prueba valida SmartPyme -> BEM.
- El retorno BEM -> SmartPyme requiere webhook público configurado en BEM.
- En modo MCP, la frontera es SmartPyme -> MCP -> BEM.
