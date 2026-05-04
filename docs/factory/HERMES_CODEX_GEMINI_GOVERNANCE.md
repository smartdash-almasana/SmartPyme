# HERMES + CODEX + GEMINI GOVERNANCE — SmartPyme Factory

## Estado
CANONICO v2

**Actualizado:** 2026-05-04 — refleja runtime real con DeepSeek v3.2 como agente operativo primario.

## Objetivo

Definir la gobernanza multiagente de SmartPyme Factory con **DeepSeek v3.2** como agente operativo primario (orquestación, lectura, construcción, auditoría), **Gemini 2.5 Pro** como fallback automático, y **Codex** como builder externo bajo demanda explícita.

**Nota:** Este documento define la gobernanza conceptual de roles. El runtime real de modelos está en `AI_PROVIDER_ROUTING_CONTRACT.md` (CANONICO v2).

---

## 1. Principio rector

**DeepSeek v3.2** es el agente operativo primario. **Gemini 2.5 Pro** es fallback automático. **Codex** es builder externo bajo demanda.

Ningún agente decide solo el cierre de un ciclo.

---

## 2. Roles

### DeepSeek v3.2 — Agente operativo primario (vía Hermes)
Responsabilidades:
- lectura, auditoría, construcción y orquestación de tareas
- elegir una unidad pequeña por ciclo
- exigir evidencia
- bloquear si falta validación
- consolidar resultado final

Uso preferente:
- ciclo normal Hermes (default)
- lectura corta y larga
- auditoría documental
- construcción de código y tests
- resumen de salida operativa

No debe:
- declarar éxito sin evidencia
- depender de memoria conversacional
- decidir cierre de ciclo sin evidencia trazable

---

### Gemini 2.5 Pro — Fallback automático / Architect
Responsabilidades:
- tomar el control si DeepSeek falla (rate limit, timeout, error 529/503)
- analizar coherencia arquitectónica
- revisar specs y contratos
- detectar deriva conceptual
- proponer priorización

**Objetivo profesional:** migrar el fallback de Gemini vía OpenRouter a Gemini directo para eliminar el punto único de falla en OpenRouter.

- **Camino preferido:** Gemini vía **Vertex AI** con ADC (`gcloud auth application-default print-access-token`).
- **Camino alternativo:** Gemini vía **Google AI Studio / Gemini API** (`GEMINI_API_KEY` o `GOOGLE_API_KEY`).
- **Estado actual:** ninguno de los dos caminos está activo como provider Hermes. Son el objetivo profesional.

No debe:
- tocar código core sin builder
- validar su propia propuesta sin evidencia externa
- reemplazar tests deterministas

---

### Codex — Builder externo (bajo demanda)
Responsabilidades:
- modificar código en refactors delicados
- crear tests con suite automatizada
- producir diff verificable
- generar evidencia técnica

Uso:
- solo bajo demanda explícita del Owner
- no es provider activo de Hermes
- se invoca desde fuera del runtime Hermes

No debe:
- inventar arquitectura de negocio
- cambiar contratos canónicos sin task explícita
- cerrar ciclos sin tests cuando toca código

---

### Hermes Gateway — Runtime / Plataforma
Responsabilidades:
- ejecutar el modelo configurado (DeepSeek v3.2 o fallback)
- leer tasks, hallazgos pending, roadmap y TECH_SPEC_QUEUE
- exigir evidencia
- consolidar resultado final

Hermes es la **plataforma**, no el modelo. El modelo activo es DeepSeek v3.2.

---

## 3. Flujo canónico por ciclo

```text
TECH_SPEC_QUEUE / TASK / HALLAZGO
        ↓
DeepSeek v3.2 selecciona unidad (vía Hermes)
        ↓
DeepSeek v3.2 ejecuta (lectura / auditoría / construcción)
        ↓
        └── (si falla) → Gemini 2.5 Pro (fallback automático)
        ↓
Tests + evidencia
        ↓
Hermes Gateway consolida decisión
        ↓
Commit / push si corresponde
```

---

## 4. Matriz de decisión

| Tipo de trabajo | Agente primario | Agente secundario |
|---|---|---|
| Ciclo normal Hermes | DeepSeek v3.2 | Gemini 2.5 Pro (fallback) |
| Código Python | DeepSeek v3.2 | Codex (bajo demanda) |
| Tests | DeepSeek v3.2 | — |
| Specs técnicas | DeepSeek v3.2 | Gemini 2.5 Pro (revisión) |
| Refactor delicado | Codex (externo) | DeepSeek v3.2 (supervisión) |
| Auditoría documental | DeepSeek v3.2 | — |
| Priorización / Backlog | DeepSeek v3.2 | Gemini 2.5 Pro |
| Runners / Scripts | DeepSeek v3.2 | — |

---

## 5. Regla de no deriva

DeepSeek no inventa estado.
Codex no define negocio (solo bajo demanda externa).
Gemini no ejecuta código crítico sin verificación.

Todo cambio debe terminar en:
- evidencia
- diff
- tests o criterio equivalente
- decisión: CORRECTO / BLOCKED / NO_VALIDADO

---

## 6. Integración con TECH_SPEC_QUEUE

DeepSeek v3.2 debe leer `docs/factory/TECH_SPEC_QUEUE.md` en cada ciclo.
Gemini 2.5 Pro debe convertir ideas nuevas en specs o tasks.
Codex solo implementa tasks ya delimitadas (bajo demanda externa).

---

## 7. Integración con hallazgos

Todo output de negocio debe respetar:

- `docs/specs/CORE_DATA_CONTRACT_AND_HALLAZGOS.md`
- entidad
- diferencia cuantificada
- comparación de fuentes
- trazabilidad

---

## 8. Criterios de aceptación de la gobernanza

- DeepSeek v3.2 es el agente operativo primario para todas las tareas.
- Gemini 2.5 Pro es fallback automático vía OpenRouter.
- Codex es builder externo bajo demanda explícita.
- Existe ruta documental para specs emergentes.
- Existe task ejecutable para implementación.
- Existe separación entre ejecución operativa y auditoría externa.
- Ningún ciclo se declara correcto sin evidencia.

---

## 9. Próxima task sugerida

Migrar el fallback de Gemini de OpenRouter a Gemini directo para eliminar el punto único de falla. Camino preferido: Vertex AI con ADC. Camino alternativo: Google AI Studio / Gemini API. Crear `factory/ai_governance/tasks/gemini_direct_fallback_migration.yaml`.
