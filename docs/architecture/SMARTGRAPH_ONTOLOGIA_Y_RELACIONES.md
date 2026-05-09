# SmartGraph — Ontología y Relaciones

## Ontología base (Node Types)
Basada en el contrato vigente del repositorio:

- TENANT
- EMPRESA
- RECEPTION_RECORD
- EVIDENCE
- DOCUMENTO
- CLIENTE
- PROVEEDOR
- PRODUCTO
- FAMILIA_DE_ARTICULOS
- CUENTA_BANCARIA
- MOVIMIENTO
- PROCESO
- EVENTO
- VARIABLE
- FORMULA
- PATOLOGIA
- SINTOMA
- PRACTICE
- TREATMENT
- MICROSERVICE
- OPERATIONAL_CASE
- FINDING
- PREGUNTA_CLINICA

## Tipos de relación (Edge Types)
- EXTRACTED_FROM
- EVIDENCE_OF
- CONFIRMADO_POR
- OBSERVADO_EN
- SOPORTA_HALLAZGO
- INFERIDO_DESDE
- INDICATES
- ACTIVA_PATOLOGIA
- REQUIRES_EVIDENCE
- REQUIRES_VARIABLE
- SE_CALCULA_CON
- SUGIERE_TRATAMIENTO
- REQUIERE_REVISION_HUMANA
- CAUSES
- AFFECTS
- DEPENDS_ON
- CONTRADICTS
- EMPEORA
- MEJORA
- DERIVA_EN

## Tipos de claim
- EXTRACTED
- INFERRED
- AMBIGUOUS
- HYPOTHESIS
- VALIDATED

## Reglas epistemológicas
- Claims INFERRED/AMBIGUOUS/HYPOTHESIS no pueden quedar `SUPPORTED` sin evidencia o revisión humana.
- Claims con `requires_human_review=true` requieren `reviewed_by` y `review_decision` para `SUPPORTED`.
- `evidence_ids` conecta claims/edges con soporte verificable.

## Aislamiento
Todas las entidades y relaciones son tenant-scoped. No hay lecturas ni escrituras cross-tenant.
