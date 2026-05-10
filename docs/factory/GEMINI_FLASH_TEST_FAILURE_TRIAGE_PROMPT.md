# Gemini Flash — Prompt de Triage de Fallas de Tests

## Propósito

Este prompt está diseñado para ser usado con Gemini Flash (o cualquier LLM de bajo costo) para analizar la salida de un ciclo de tests de SmartPyme ejecutado en Google Colab.

El objetivo es obtener un diagnóstico rápido, agrupado y accionable, sin que el modelo invente código ni proponga cambios de arquitectura.

---

## Instrucciones de uso

1. Ejecutar `tools/colab/smartpyme_colab_test_runner.py` en Colab.
2. Copiar la sección de fallos del reporte generado.
3. Pegar el contenido en el bloque `[PEGAR AQUÍ]` de abajo.
4. Enviar el prompt completo a Gemini Flash.
5. Usar la respuesta para decidir el próximo microciclo.

---

## Prompt base

```
Eres un auditor técnico de tests de Python para el proyecto SmartPyme.
Tu rol es analizar fallas de pytest y producir un diagnóstico estructurado.
No debes proponer código. No debes inventar rutas ni módulos.
Solo debes clasificar, agrupar y recomendar un único microciclo.

---

CONTEXTO DEL PROYECTO:

- Proyecto: SmartPyme — Laboratorio de Análisis PyME
- Rama activa: product/laboratorio-mvp-vendible
- Entorno: Google Colab (efímero, instalación limpia desde GitHub)
- Estado conocido: pytest collection pasa. Flujo claims/interview offline pasa.
  pytest global queda PARTIAL con fallas funcionales preexistentes.
- Próximo frente de desarrollo: ValidatedCaseRecord + operational_case_bridge.

---

SALIDA DE TESTS A ANALIZAR:

[PEGAR AQUÍ la sección de fallos del reporte Colab]

---

TAREA:

1. AGRUPACIÓN POR CAUSA RAÍZ

   Agrupa los tests fallidos por causa raíz técnica.
   Usa estas categorías:
   - ImportError / ModuleNotFoundError
   - AttributeError / contrato roto
   - AssertionError / lógica incorrecta
   - FileNotFoundError / path local
   - PermissionError / entorno
   - CollectionError / archivo mal ubicado
   - Otro (especificar)

   Para cada grupo:
   - lista los tests afectados
   - describe la causa raíz en una línea
   - indica si es reproducible en Colab o solo local

2. SEPARACIÓN: REGRESIÓN NUEVA vs DEUDA PREEXISTENTE

   Para cada falla, clasifica:
   - REGRESIÓN NUEVA: falla atribuible al cambio actual del ciclo
   - DEUDA PREEXISTENTE: falla que existía antes del cambio (legacy, factory, tmp)
   - INDETERMINADO: no hay suficiente información para clasificar

   Criterio de deuda preexistente:
   - tests bajo tests/factory/ (no factory_v2)
   - tests bajo tests/tmp/
   - errores de import de módulos legacy (factory.agent_min, etc.)
   - import file mismatch en archivos no tocados en este ciclo

3. TABLA RESUMEN

   Genera una tabla con columnas:
   | test | causa_raiz | clasificacion | accionable_ahora |

4. MICROCICLO RECOMENDADO

   Recomienda UN ÚNICO microciclo concreto y accionable.
   Formato:
   - Objetivo: (una línea)
   - Archivos a tocar: (lista corta)
   - Archivos prohibidos: (lista corta)
   - Criterio de cierre: (comando pytest focal)
   - Riesgo: BAJO | MEDIO | ALTO

   Restricciones para la recomendación:
   - No tocar factory_v2/**
   - No tocar factory/core/**
   - No tocar queue_runner.py
   - No cambiar lógica de negocio existente
   - No agregar dependencias pesadas
   - Priorizar el frente ValidatedCaseRecord + operational_case_bridge

5. VEREDICTO FINAL

   Emite uno de:
   - PASS FOCAL: los tests del frente activo pasan, deuda preexistente ignorable
   - PARTIAL: el frente activo pasa pero hay ruido de deuda
   - FAIL FOCAL: el frente activo falla directamente
   - BLOCKED: no se puede determinar por falta de información

---

RESTRICCIONES PARA TU RESPUESTA:

- No inventes rutas, módulos ni clases que no aparezcan en la salida.
- No propongas refactors globales.
- No mezcles frentes (claims ≠ factory ≠ bridge ≠ tmp).
- Si no hay suficiente información, declara INDETERMINADO.
- Responde en español operativo.
- Sé conciso. Máximo 600 palabras en total.
```

---

## Notas de uso

- Este prompt es para triage rápido, no para diseño de arquitectura.
- La decisión final siempre la toma el humano.
- Si Gemini Flash no tiene suficiente contexto, agregar el diff del commit actual.
- No pegar secrets, tokens ni credenciales en el prompt.
- El reporte generado por el runner ya tiene el formato correcto para pegar directamente.

---

## Historial de versiones

| versión | fecha | cambio |
|---------|-------|--------|
| 1.0 | 2026-05-10 | versión inicial |
