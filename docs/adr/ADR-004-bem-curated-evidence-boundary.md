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

## Proximos artefactos

- BemWebhookPayload.
- BemCuratedEvidenceAdapter.
- CuratedEvidenceRecord.
- EvidenceValidationService.
- POST /webhooks/bem.
- MCP tool `bem_submit_workflow`.
- BemRunRepository.

Primer smoke test objetivo:

```text
fake BEM payload
-> webhook SmartPyme
-> adapter
-> CuratedEvidenceRecord persistido
```

Smoke MCP objetivo:

```text
bem_submit_workflow
-> BEM
-> BemRunRepository
-> response_payload persistido
```
