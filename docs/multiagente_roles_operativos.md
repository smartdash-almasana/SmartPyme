# Roles Operativos del Ciclo Multiagente

Ningún agente valida su propio trabajo.

## Architect
Diseña hallazgos y los deja en `factory/hallazgos/pending`.

## Builder
Ejecuta únicamente los cambios permitidos por el hallazgo asignado.

## Auditor
Valida evidencia contra los criterios de cierre.

## Protocolo obligatorio
Write → Verify → Report

Si no hay evidencia verificable, el estado es NO VALIDADO.
