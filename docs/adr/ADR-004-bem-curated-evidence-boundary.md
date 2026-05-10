# ADR-004 — BEM Curated Evidence Boundary

## Estado

Accepted

## Contexto

SmartPyme es el motor operacional soberano del MVP. Su responsabilidad principal es recibir evidencia estructurada, validar suficiencia, producir hallazgos accionables y construir diagnosticos operacionales trazables por tenant.

Para el MVP vendible, la ingestion y curado de documentacion cruda queda fuera de SmartPyme. Esa capa sera resuelta por BEM mediante API o webhook.

## Decision

BEM sera la capa externa de ingestion y curado documental.

SmartPyme recibira evidencia ya curada y estructurada.

Frontera oficial:

```text
Documento crudo -> BEM
Evidencia curada -> SmartPyme
```

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

## Flujo MVP

```text
Cliente
-> UI o chatbot SmartPyme
-> upload de documentacion
-> BEM workflow
-> output BEM por API o webhook
-> CuratedEvidenceRecord en SmartPyme
-> EvidenceValidationService
-> OperationalClaim / Finding
-> DiagnosticReport
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

Riesgos:

- Dependencia externa de BEM.
- Cambios en API o webhook.
- Costos variables por procesamiento documental.

Mitigacion:

- Adapter explicito.
- Contratos internos soberanos.
- Persistencia del payload recibido.
- Fail-closed si falta evidencia o confianza suficiente.

## Proximos artefactos

- BemWebhookPayload.
- BemCuratedEvidenceAdapter.
- CuratedEvidenceRecord.
- EvidenceValidationService.
- POST /webhooks/bem.

Primer smoke test objetivo:

```text
fake BEM payload
-> webhook SmartPyme
-> adapter
-> CuratedEvidenceRecord persistido
```
