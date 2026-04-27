# HALLAZGO

## META
- id: HZ-2026-04-27-FACTORY-005
- estado: pending
- modulo_objetivo: tabular-processing
- prioridad: alta
- origen: gpt-auditor
- repo_destino: SmartPyme

## OBJETIVO
Incorporar Polars como motor tabular preferente para SmartPyme en tareas de ingesta, normalizacion y procesamiento de datos estructurados.

## CONTEXTO
SmartPyme procesara Excel, CSV, exports, tablas de documentos y evidencia estructurada. Polars debe quedar definido como herramienta preferente para dataframes por rendimiento, expresividad y manejo de datos grandes.

## RUTAS_OBJETIVO
Se permite crear o modificar solo:

- docs/specs/08-tabular-processing.md
- docs/guias/polars-guidelines.md
- factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md

## RESTRICCIONES
- No tocar app/**
- No tocar core/**
- No tocar services/**
- No tocar tests/**
- No modificar codigo Python
- No agregar dependencias todavia
- No reemplazar pandas si existe
- No hacer refactors

## TAREAS_EJECUCION

1. Crear `docs/specs/08-tabular-processing.md`.
2. Definir Polars como motor tabular preferente para:
   - CSV
   - Excel convertido a tablas
   - exports de sistemas
   - normalizacion de facts
   - conciliacion y comparacion tabular
3. Crear `docs/guias/polars-guidelines.md`.
4. Documentar reglas:
   - usar LazyFrame cuando aplique
   - mantener tenant_id en todo procesamiento multi-tenant
   - no mezclar tenants
   - conservar source_ref/evidence_id
   - no perder tipos, unidades ni moneda
   - reportar confianza y errores de parseo
5. Ajustar el skill Hermes SmartPyme Factory para que Builder considere Polars en tareas tabulares futuras.

## CRITERIOS_DE_ACEPTACION
- Existe `docs/specs/08-tabular-processing.md`.
- Existe `docs/guias/polars-guidelines.md`.
- Ambos mencionan `polars`.
- Las guias mencionan `tenant_id`.
- Las guias mencionan `evidence_id` o `source_ref`.
- El skill Hermes menciona Polars para procesamiento tabular.
- No se modifica codigo Python.
- No se agregan dependencias todavia.

## VALIDACIONES

```bash
git diff --name-only
grep -R "Polars\|polars" -n docs/specs/08-tabular-processing.md docs/guias/polars-guidelines.md factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md
grep -R "tenant_id" -n docs/specs/08-tabular-processing.md docs/guias/polars-guidelines.md
grep -R "evidence_id\|source_ref" -n docs/specs/08-tabular-processing.md docs/guias/polars-guidelines.md
```

## SALIDA_BUILDER
Debe reportar:

- archivos creados o modificados
- reglas tabulares documentadas
- validaciones ejecutadas
- git diff --name-only

## SALIDA_AUDITOR
Debe validar:

- alcance respetado
- no se modifico codigo Python
- no se agregaron dependencias
- Polars queda definido como estandar tabular futuro
- veredicto VALIDADO o NO_VALIDADO
