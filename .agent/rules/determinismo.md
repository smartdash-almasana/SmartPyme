# Reglas de Determinismo y Precisión

Este archivo gobierna el comportamiento determinístico del core de la factoría SmartPyme.

## 1. Lógica Fiscal y Monetaria
Estrictamente prohibido el uso de `float` en cálculos monetarios, fiscales, o impositivos. 
Se debe usar de forma excluyente `decimal.Decimal` nativo de Python, con una precisión mínima configurada en `28` (por defecto en contextos generales, pero asegurado).

## 2. Bloqueo de Ambigüedad
Toda ambigüedad algorítmica, incertidumbre en los datos o falta de confirmación sobre la fuente de la verdad bloquea inmediatamente la transición de estado bajo el estado `AWAITING_VALIDATION`.

## 3. Protocolo de Hallazgos Operativos
No se puede emitir, registrar ni generar ningún hallazgo analítico o clínico sin que presente de forma mandatoria:
- Entidad afectada explícita.
- Diferencia cuantificada.
- Comparación clara de orígenes.
- Fuente auditable debidamente citada.
