# Smoke manual — BEM simulado a diagnóstico SmartPyme

## Objetivo

Validar manualmente el flujo operativo MVP:

```text
payload BEM simulado
-> webhook SmartPyme
-> persistencia soberana
-> diagnostico operacional
-> informe Markdown
```

Esta prueba no requiere API key de BEM porque no invoca BEM real. Simula el output curado que SmartPyme espera recibir por webhook.

---

## Precondición

Desde la raíz del repo:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

La API debe quedar disponible en:

```text
http://127.0.0.1:8000
```

---

## 1. Enviar evidencia BEM simulada

## Smoke rápido con fixture

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/webhooks/bem" \
  -H "Content-Type: application/json" \
  -d @docs/operational/fixtures/bem_payload_venta_bajo_costo.json
```

---

## Submit manual hacia BEM

- Requiere `BEM_API_KEY` real.
- Requiere `workflow_id` real de BEM.
- No se ejecuta en smoke local.

Comando:

```bash
python tools/bem_submit_payload.py \
  --workflow-id "<BEM_WORKFLOW_ID>" \
  --payload-file docs/operational/fixtures/bem_payload_venta_bajo_costo.json
```

Variante con API key explícita:

```bash
python tools/bem_submit_payload.py \
  --workflow-id "<BEM_WORKFLOW_ID>" \
  --payload-file docs/operational/fixtures/bem_payload_venta_bajo_costo.json \
  --api-key "<BEM_API_KEY>"
```

Resultado esperado:
- JSON de respuesta de BEM impreso en formato pretty.

Aclaración:
- Este comando prueba salida SmartPyme -> BEM.
- El smoke webhook prueba entrada BEM -> SmartPyme.

---

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/webhooks/bem" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "acme-demo",
    "payload": {
      "evidence_id": "ev-demo-001",
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
  }'
```

Respuesta esperada:

```json
{
  "status": "accepted",
  "tenant_id": "acme-demo",
  "evidence_id": "ev-demo-001"
}
```

---

## 2. Consultar diagnóstico operacional

```bash
curl "http://127.0.0.1:8000/api/v1/diagnostico/acme-demo"
```

Respuesta esperada:

```json
{
  "tenant_id": "acme-demo",
  "findings": [
    {
      "finding_type": "VENTA_BAJO_COSTO",
      "severity": "HIGH",
      "message": "precio_venta (10.0) es menor que costo_unitario (80.0). Se está vendiendo por debajo del costo.",
      "evidence_id": "ev-demo-001"
    }
  ],
  "evidence_count": 1
}
```

---

## 3. Consultar informe Markdown

```bash
curl "http://127.0.0.1:8000/api/v1/diagnostico/acme-demo/informe"
```

Respuesta esperada:

```markdown
# Diagnóstico Operacional

**Tenant:** acme-demo
**Cantidad de evidencias:** 1

## Hallazgos

### VENTA_BAJO_COSTO

- **Severidad:** HIGH
- **Mensaje:** precio_venta (10.0) es menor que costo_unitario (80.0). Se está vendiendo por debajo del costo.
- **Evidence ID:** ev-demo-001
```

---

## 4. Descargar informe Markdown con nombre explícito

Algunos clientes `curl` no respetan automáticamente el filename de `Content-Disposition` cuando se usa una URL terminada en `/informe`.

Usar nombre explícito:

```bash
curl -L "http://127.0.0.1:8000/api/v1/diagnostico/acme-demo/informe" -o diagnostico-acme-demo.md
```

Verificar:

```bash
cat diagnostico-acme-demo.md
```

El archivo debe contener el hallazgo:

```text
VENTA_BAJO_COSTO
```

---

## Notas operativas

- Esta prueba usa payload BEM simulado.
- No requiere API key de BEM.
- No prueba upload real de archivos.
- No prueba workflow real de BEM.
- Valida únicamente el lado SmartPyme del contrato: recepción, persistencia, diagnóstico e informe.
- Si se reutiliza el mismo `evidence_id` contra la misma base SQLite, puede aparecer conflicto por duplicado. Para repetir la prueba, usar otro `evidence_id` o limpiar la base local de prueba.

---

## Resultado validado

En VM se validó el flujo:

```text
POST /api/v1/webhooks/bem -> 200 OK
GET /api/v1/diagnostico/acme-demo -> 200 OK con VENTA_BAJO_COSTO
GET /api/v1/diagnostico/acme-demo/informe -> 200 OK con Markdown
```
