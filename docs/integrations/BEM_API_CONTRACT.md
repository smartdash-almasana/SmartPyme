# BEM API and MCP Integration Contract

**Status:** Draft operativo

## Fuentes revisadas

- BEM SDKs: `https://docs.bem.ai/guide/sdks`
- BEM MCP Server: `https://docs.bem.ai/guide/mcp-server`
- SmartPyme client: `app/services/bem_client.py`
- SmartPyme CLI submit tool: `tools/bem_submit_payload.py`
- Fixture operativo: `docs/operational/fixtures/bem_payload_venta_bajo_costo.json`

## Contrato oficial BEM observado

BEM expone tres recursos principales en sus SDKs:

- `functions`
- `workflows`
- `calls`

El MCP oficial de BEM se instala/ejecuta como:

```bash
npx -y bem-ai-sdk-mcp
```

El MCP oficial expone herramientas generales:

- `docs`: búsqueda de documentación BEM.
- `code`: ejecución segura de TypeScript contra el SDK BEM.

## Autenticación

BEM requiere API key.

- Header HTTP: `x-api-key`
- Variable de entorno esperada: `BEM_API_KEY`

Reglas SmartPyme:

- Nunca imprimir `BEM_API_KEY`.
- Nunca persistir `BEM_API_KEY` en archivos versionados.
- El MCP oficial o el runtime deben recibirla por entorno/secret manager.

## Base URL

Base URL oficial confirmada para la integración actual:

```text
https://api.bem.ai
```

Reglas:

- `BEM_BASE_URL` puede existir para override operacional.
- Si `BEM_BASE_URL` no existe, SmartPyme debe usar `https://api.bem.ai`.
- Valores truncados como `https://api.bem` son inválidos y producen error DNS.

## Endpoint SmartPyme actual

`app/services/bem_client.py` ejecuta workflows con:

```text
POST /v3/workflows/{workflow_id}/call?wait=true
```

Cuerpo enviado por SmartPyme:

```json
{
  "input": { }
}
```

Headers:

```text
x-api-key: <secret>
content-type: application/json
```

## Functions vs Workflows

### Functions

Las functions son primitivas de procesamiento declaradas en BEM. Ejemplo oficial provisto:

```python
from bem import Bem

client = Bem()
client.functions.create(...)
```

Crear functions es provisioning remoto y no debe ocurrir durante pruebas de runtime sin aprobación explícita.

### Workflows

Los workflows son unidades de orquestación/DAG. SmartPyme actualmente está alineado a workflows y usa `BEM_WORKFLOW_ID`.

Decisión actual:

```text
SmartPyme mantiene integración por Workflows.
```

No migrar a Functions salvo que la documentación privada del workflow indique que el MVP requiere operar por function calls directas.

## Variables de entorno requeridas

- `BEM_API_KEY`: obligatoria.
- `BEM_WORKFLOW_ID`: obligatoria para submit workflow.
- `BEM_BASE_URL`: opcional; default `https://api.bem.ai`.
- `WEBHOOK_BEM`: requerido solo para callbacks/webhooks si el flujo lo usa.

## Fixture operativo actual

Archivo:

```text
docs/operational/fixtures/bem_payload_venta_bajo_costo.json
```

Forma actual:

```json
{
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
```

Este payload es válido para SmartPyme. Todavía debe validarse contra el input schema real del workflow BEM `BEM_WORKFLOW_ID`.

## Causa probable del HTTP 400 actual

Conectividad ya confirmada contra BEM cuando la URL base es correcta. Un HTTP 400 en:

```text
/v3/workflows/{BEM_WORKFLOW_ID}/call?wait=true
```

significa que al menos una de estas condiciones puede ser cierta:

- `BEM_WORKFLOW_ID` existe pero espera otro input schema.
- `BEM_WORKFLOW_ID` no corresponde al workflow SmartPyme esperado.
- El workflow espera archivo multipart y no payload JSON.
- El wrapper `{"input": payload}` no coincide con el contrato del workflow.
- El workflow requiere campos adicionales no presentes en el fixture.

## Uso correcto del MCP oficial de BEM

Antes de nuevos submits reales, usar el MCP oficial para:

1. Consultar documentación sobre workflow calls.
2. Inspeccionar recursos de workflows/calls si el SDK lo permite.
3. Determinar el schema esperado por `BEM_WORKFLOW_ID`.
4. Verificar si el workflow requiere payload JSON o file multipart.

Prohibido durante esta fase:

- Crear functions.
- Crear workflows.
- Ejecutar calls mutantes sin aprobación.
- Modificar datos remotos de BEM.

## SmartPyme MCP propio

SmartPyme puede tener MCP propio, pero no reemplaza el MCP oficial de BEM.

Capas:

```text
BEM MCP oficial
→ operar/documentar recursos BEM: functions, workflows, calls.

SmartPyme MCP propio
→ exponer capacidades soberanas: evidencia, diagnóstico, hallazgos, submit controlado.
```

Tools candidatas SmartPyme MCP:

- `smartpyme.bem.healthcheck`
- `smartpyme.bem.submit_workflow`
- `smartpyme.evidence.list_curated`
- `smartpyme.diagnostic.run_for_tenant`
- `smartpyme.diagnostic.get_report`

Reglas MCP SmartPyme:

- No contener lógica de negocio nueva.
- Reusar servicios existentes.
- `tenant_id` obligatorio en tools de datos.
- Fail-closed si falta `tenant_id`.
- No exponer queries cross-tenant.
- No imprimir secrets.
- `workflow_id` no debe ser libre por defecto; usar `BEM_WORKFLOW_ID` o allowlist.

## Plan de validación posterior

1. Usar BEM MCP oficial para confirmar contrato de input del workflow configurado.
2. Ajustar fixture o modo de submit si el workflow espera otra forma.
3. Ejecutar una única prueba real controlada.

## Preguntas abiertas

- ¿El workflow `BEM_WORKFLOW_ID` configurado espera JSON o archivo multipart?
- ¿El input correcto debe ir bajo `input`, bajo otro campo o directo en body?
- ¿El workflow configurado es realmente `smartpyme-venta-bajo-costo`?
- ¿Cómo se consulta formalmente el schema del workflow desde SDK/MCP?
