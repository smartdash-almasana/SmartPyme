# BEM Real XLSX Smoke

## Flujo validado

XLSX -> `tools/bem_submit_payload.py --file` -> respuesta BEM (envelope) -> `raw["call"]` -> `BemCuratedEvidenceAdapter` -> `CuratedEvidenceRepository` -> `BasicOperationalDiagnosticService` -> findings.

Smoke real validado con hallazgo: `VENTA_BAJO_COSTO`.

## Variables necesarias

- `BEM_API_KEY`
- `BEM_WORKFLOW_ID`

## Comando PowerShell exacto (submit XLSX a BEM)

```powershell
$env:PYTHONPATH='.'
python tools/bem_submit_payload.py --workflow-id $env:BEM_WORKFLOW_ID --api-key $env:BEM_API_KEY --file <RUTA_XLSX> --call-reference-id smoke-xlsx-bem-001
```

## Estructura esperada de respuesta

El smoke de diagnóstico consume `raw["call"]` (no el JSON envelope completo).

- Envelope (ejemplo conceptual):
  - `raw`: objeto raíz persistido localmente
  - `raw["call"]`: payload BEM usable por `BemCuratedEvidenceAdapter`

Aclaración clave:

- `transformedContent` vive en `call.outputs[*].transformedContent`.

## Hallazgo esperado

Con dataset de prueba compatible, se espera al menos:

- `VENTA_BAJO_COSTO`

## Envelope `call` (explicación breve)

Algunos flujos guardan metadata alrededor de la llamada real a BEM. El adapter actual espera el objeto de llamada BEM directamente (`call`) con la estructura de `outputs`. Por eso, cuando existe envelope, el input correcto al adapter es `raw["call"]`.

## Cómo sanitizar respuesta

Antes de compartir evidencia:

- remover o enmascarar API keys/tokens/headers
- remover URLs firmadas o IDs sensibles
- conservar solo campos técnicos mínimos para diagnóstico:
  - `callReferenceID` / `callID`
  - `outputs[*].transformedContent` (si aplica)
  - tipos de hallazgo resultantes

## Cómo repetir smoke sin exponer credenciales

1. Definir credenciales solo en variables de entorno de sesión (`$env:BEM_API_KEY`, `$env:BEM_WORKFLOW_ID`).
2. Ejecutar submit por CLI sin imprimir variables.
3. Guardar respuesta en archivo local temporal.
4. Procesar adapter con `raw["call"]` y reportar solo:
   - total findings
   - codes
   - evidence_ids
   - payload keys usados

## Limitaciones actuales

- El adapter falla si no existe `outputs` en el objeto que recibe.
- Si la respuesta viene con envelope, hay que extraer `raw["call"]` manualmente para este smoke.
- El smoke no reemplaza el camino BEM productivo end-to-end con webhook; valida compatibilidad de estructura y reglas diagnósticas.
- En Windows puede aparecer `PermissionError` al limpiar SQLite temporal; no invalida el resultado del smoke si los findings ya fueron emitidos.
