# ADR-004 — BEM Curated Evidence Boundary

## Estado

Accepted

## Contexto

SmartPyme es el motor operacional soberano del MVP. Su responsabilidad principal es recibir evidencia estructurada, validar suficiencia, producir hallazgos accionables y construir diagnosticos operacionales trazables por tenant.

Para el MVP vendible, la ingestion y curado de documentacion cruda queda fuera de SmartPyme. Esa capa sera resuelta por BEM mediante API, webhook o tool MCP controlada.

## Decision

BEM sera la capa externa de ingestion y curado documental.

SmartPyme recibira evidencia ya curada y estructurada.

Frontera oficial:

```text
Documento crudo -> BEM
Evidencia curada -> SmartPyme
```

La invocacion SmartPyme -> BEM puede ejecutarse mediante:

- API directa.
- Webhook.
- Tool MCP `bem_submit_workflow`.

La herramienta MCP no modifica la soberania del dominio SmartPyme. Solo encapsula el envio controlado hacia BEM.

## Responsabilidades de BEM

- Recibir documentos crudos.
- Extraer datos estructurados.
- Clasificar documentos.
- Normalizar payloads.
- Entregar JSON curado.
- Informar metadata y confianza cuando este disponible.
- Enviar resultados por API o webhook.

## Responsabilidades de SmartPyme

- Asociar tenant_id.
- Registrar ReceptionRecord.
- Registrar EvidenceRecord o CuratedEvidenceRecord.
- Validar suficiencia de evidencia.
- Interpretar sintomas operacionales.
- Construir OperationalClaim y hallazgos.
- Generar DiagnosticReport.
- Preservar trazabilidad y fail-closed.
- Registrar runs externos BEM.

## Flujo MVP

```text
Cliente
-> UI o chatbot SmartPyme
-> upload de documentacion
-> BEM workflow
-> output BEM por API, webhook o adapter MCP
-> CuratedEvidenceRecord en SmartPyme
-> EvidenceValidationService
-> OperationalClaim / Finding
-> DiagnosticReport
```

## Flujo MCP alineado

```text
Gateway/Hermes autorizado
-> SmartPyme MCP Bridge
-> bem_submit_workflow
-> BemSubmitService
-> BEM
-> response_payload
-> BemRunRepository
-> adapter BEM response -> CuratedEvidenceRecord
```

## Queda fuera de SmartPyme en el MVP

- OCR propietario.
- Parsing documental pesado.
- Motor interno complejo de Excel.
- Extraccion multimodal propia.
- Curado documental completo.
- Clasificacion documental avanzada.

## Queda dentro de SmartPyme

- Contratos para recibir payloads curados de BEM.
- Adapter BEM -> evidencia SmartPyme.
- Persistencia soberana por tenant.
- Persistencia de runs BEM.
- Validacion operacional de evidencia.
- Hallazgos accionables.
- Diagnostico operacional.

## Consecuencias

Beneficios:

- MVP mas pequeno.
- Menor complejidad.
- Foco correcto en interpretacion operacional.
- Menor deuda tecnica.
- Mejor salida temprana a calle.
- Frontera MCP explicita y controlada.

Riesgos:

- Dependencia externa de BEM.
- Cambios en API o webhook.
- Costos variables por procesamiento documental.
- Fallas de integracion MCP.

Mitigacion:

- Adapter explicito.
- Contratos internos soberanos.
- Persistencia del payload recibido.
- Fail-closed si falta evidencia o confianza suficiente.
- Persistencia de runs BEM antes de promover evidencia.

## Estado de integración (cierre actual)

Implementado:

- Submit directo SmartPyme -> BEM (HTTP) con tracking de runs.
- Submit SmartPyme -> MCP -> BEM con adapter tenant-aware.
- Persistencia de runs en `BemRunRepository` (`data/bem_runs.db` por defecto).
- `BemCuratedEvidenceAdapter.build_curated_evidence_from_bem_response(...)` mapea `response_payload` real de BEM a `CuratedEvidenceRecord`.
- `BemSubmitService` promueve automáticamente `CuratedEvidenceRecord` si se inyecta `CuratedEvidenceRepositoryBackend`.
- HTTP router (`POST /api/v1/bem/submit`) inyecta `CuratedEvidenceRepositoryBackend` por defecto (`data/curated_evidence.db` o `SMARTPYME_CURATED_EVIDENCE_DB_PATH`).
- MCP bridge (`bem_submit_workflow`) inyecta `CuratedEvidenceRepositoryBackend` por defecto.

Componentes clave:

- `BemSubmitPort`
- `BemMcpSubmitAdapter`
- `BemSubmitService` con soporte HTTP directo, MCP tenant-aware y promoción opcional a evidencia curada.
- `BemCuratedEvidenceAdapter` con método `build_curated_evidence_from_bem_response`.
- `CuratedEvidenceRepositoryBackend` (`data/curated_evidence.db` por defecto).

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
- `source_metadata.source_name` / `source_type`: desde `transformedContent`
- `confidence`: desde `avgConfidence` si existe
- `tenant_id`: preservado desde contexto del run

Resultado de validación integral:

- Suite específica: `56 passed` (adapter + servicio + router + MCP bridge).

## Proximos artefactos

- ~~BemWebhookPayload.~~ (implementado)
- ~~BemCuratedEvidenceAdapter.~~ (implementado)
- ~~CuratedEvidenceRecord.~~ (implementado)
- ~~BemRunRepository.~~ (implementado)
- EvidenceValidationService — conectar `CuratedEvidenceRecord` al diagnóstico operacional.
- POST /webhooks/bem — webhook externo BEM → SmartPyme (flujo inverso).
- MCP tool `bem_submit_workflow` — ya operativo con persistencia curada.
