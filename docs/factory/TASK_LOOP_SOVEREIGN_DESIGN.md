# SmartPyme Factory — Diseño del TaskLoop Soberano

**Versión:** 1.0  
**Capa:** FACTORY_PROTOCOL  
**Fase:** DOCUMENTAR  
**Modo:** DOC_ONLY  
**Fecha:** Mayo 2026  
**Rama:** factory/ts-006-jobs-sovereign-persistence

---

## Propósito

Este documento define el diseño operativo del TaskLoop soberano de SmartPyme Factory.

El TaskLoop soberano es el ciclo de trabajo que convierte TaskSpecs pendientes en código, evidencia y cierre, respetando la gobernanza de capas, fases, modos y ejecutores.

---

## 1. Principio rector

```text
Una tarea por ciclo.
Un ejecutor por tarea.
Un frente activo a la vez.
```

El TaskLoop no es un runner autónomo. Es un protocolo de coordinación entre ejecutores humanos y agentes, gobernado por el owner.

---

## 2. Alcance

El TaskLoop soberano opera sobre:

```text
Repo principal:   SmartPyme (GitHub)
Config VM:        Hermes / configuración de la VM de producción
```

El TaskLoop **no opera** sobre:

```text
Infraestructura de terceros sin TaskSpec explícita
Bases de datos de producción sin gate validado
Secretos o .env sin autorización explícita del owner
```

---

## 3. Ejecutores autorizados

| Ejecutor | Rol | Puede commit/push | Disponibilidad |
|---|---|---|---|
| `KIRO_LOCAL` | Builder principal — código, contratos, tests, docs | ✅ Sí | Martes, jueves, sábado, domingo |
| `HERMES` | Orquestador VM — ciclos automatizados, git, evidencia | ✅ Sí (vía gateway) | Todos los días |
| `GPT_COPILOTO_CHAT` | Arquitecto / auditor externo — diseño, specs, decisiones | ❌ No | Todos los días |
| `GPT_COPILOTO_GITHUB` | Builder GitHub Copilot — código en PR/branch | ✅ Sí | Todos los días |
| `GEMINI_GOOGLE` | Auditor semántico — coherencia documental, análisis largo | ❌ No | Todos los días |

### Regla de commit/push

Solo `KIRO_LOCAL`, `HERMES` y `GPT_COPILOTO_GITHUB` pueden hacer commit y push.

`GPT_COPILOTO_CHAT` y `GEMINI_GOOGLE` producen propuestas, specs y análisis. No modifican el repo directamente.

---

## 4. Calendario de disponibilidad

| Día | Ejecutor principal | Fallback |
|---|---|---|
| Lunes | `HERMES` | `GPT_COPILOTO_GITHUB`, `GEMINI_GOOGLE` |
| Martes | `KIRO_LOCAL` | `HERMES`, `GPT_COPILOTO_GITHUB` |
| Miércoles | `HERMES` | `GPT_COPILOTO_GITHUB`, `GEMINI_GOOGLE` |
| Jueves | `KIRO_LOCAL` | `HERMES`, `GPT_COPILOTO_GITHUB` |
| Viernes | `HERMES` | `GPT_COPILOTO_GITHUB`, `GEMINI_GOOGLE` |
| Sábado | `KIRO_LOCAL` | `HERMES` |
| Domingo | `KIRO_LOCAL` | `HERMES` |

### Regla de fallback

Si el ejecutor principal no está disponible:

```text
1. Intentar con el primer fallback de la lista.
2. Si ningún fallback puede ejecutar la tarea: BLOCKED_EXECUTOR_UNAVAILABLE.
3. Registrar el bloqueo en factory/control/FACTORY_STATUS.md.
4. No avanzar hasta que el owner desbloquee o cambie el ejecutor.
```

`BLOCKED_EXECUTOR_UNAVAILABLE` no es un error. Es un estado válido que protege la integridad del ciclo.

---

## 5. Estructura del ciclo

Cada ciclo del TaskLoop sigue este flujo:

```text
1. PRECHECK
   → git branch --show-current
   → git status -s
   → Verificar que el worktree está limpio o justificado
   → Si BLOCKED_DIRTY_WORKTREE: detener

2. SELECCIÓN DE TAREA
   → Leer factory/ai_governance/tasks/*.yaml
   → Seleccionar UNA tarea con status=pending
   → Validar contra factory/ai_governance/taskspec.schema.json
   → Si no hay tarea pending: IDLE (no es error)
   → Si la TaskSpec no cumple schema: BLOCKED_SCHEMA_INVALID

3. VERIFICACIÓN DE MODO Y EJECUTOR
   → Confirmar que operational_mode es válido
   → Confirmar que model_target es compatible con el ejecutor del día
   → Si falta modo: BLOCKED_MODE_MISSING
   → Si modo inválido: BLOCKED_MODE_INVALID
   → Si ejecutor no disponible: BLOCKED_EXECUTOR_UNAVAILABLE

4. VERIFICACIÓN DE GATE
   → Leer factory/control/AUDIT_GATE.md
   → Si gate = WAITING_AUDIT, BLOCKED, HOLD o PAUSED: detener
   → Solo avanzar si gate = APPROVED, OPEN o RUN

5. EJECUCIÓN
   → Respetar allowed_files y forbidden_files
   → Ejecutar solo lo que el operational_mode permite
   → ANALYSIS_ONLY: solo lectura, sin escritura
   → WRITE_AUTHORIZED: escritura solo en allowed_files
   → Ejecutar required_tests

6. EVIDENCIA
   → Guardar en factory/evidence/<task_id>/
   → Mínimo: cycle.md, commands.txt, git_status.txt, git_diff.patch, tests.txt, decision.txt

7. CIERRE
   → Actualizar status de la TaskSpec a submitted o blocked
   → Actualizar gate a WAITING_AUDIT
   → Commit + push si el ejecutor tiene permiso
   → Reportar al owner

8. AUDITORÍA (ciclo siguiente o externo)
   → GPT_COPILOTO_CHAT o GEMINI_GOOGLE revisan evidencia
   → Emiten APPROVED, REJECTED, BLOCKED o NO_VALIDADO
   → Owner decide si continuar, corregir o pausar
```

---

## 6. Regla anti-deriva

```text
El NEXT_STEP del agente nunca cambia el FRENTE_ACTIVO.
```

### Definición de FRENTE_ACTIVO

El frente activo es la capa y fase que está en ejecución en el ciclo actual.

Ejemplo:

```text
FRENTE_ACTIVO: CAPA_03 / FASE_CONTRATAR
```

### Qué puede hacer NEXT_STEP

```text
✅ Proponer la siguiente TaskSpec dentro del mismo frente activo
✅ Proponer auditoría del trabajo realizado
✅ Proponer documentación del cierre
✅ Declarar BLOCKED con razón explícita
```

### Qué NO puede hacer NEXT_STEP

```text
❌ Abrir una nueva capa sin cierre explícito de la actual
❌ Cambiar la fase activa sin gate validado
❌ Proponer trabajo en múltiples frentes simultáneos
❌ Sugerir integración con infraestructura no autorizada
❌ Proponer cambios en contratos de capas ya cerradas
```

### Consecuencia de deriva

Si un agente propone en NEXT_STEP algo que cambia el frente activo sin autorización:

```text
BLOCKED_SCOPE_EXPANSION
```

El owner debe decidir explícitamente si acepta el cambio de frente.

---

## 7. Frente activo vigente

```text
FRENTE_ACTIVO: CAPA_03 / FASE_IMPLEMENTAR
RAMA: factory/ts-006-jobs-sovereign-persistence
ESTADO: en progreso
```

Tareas completadas en este frente:

```text
TS_030_001_CONTRATO_OPERATIONAL_CASE_V2   → DONE
TS_030_002_SERVICIO_APERTURA_CASO         → DONE
```

Próximas tareas en este frente:

```text
TS_030_003_INTEGRACION_CAPA_03            → pending (ANALYSIS_ONLY primero)
```

---

## 8. Gestión de bloqueos

| Bloqueo | Causa | Acción |
|---|---|---|
| `BLOCKED_EXECUTOR_UNAVAILABLE` | Ejecutor principal no disponible y fallbacks no aplican | Registrar en FACTORY_STATUS.md; esperar al owner |
| `BLOCKED_DIRTY_WORKTREE` | git status no limpio sin justificación | Limpiar worktree o justificar antes de continuar |
| `BLOCKED_WRONG_BRANCH` | No está en la rama autorizada | Cambiar a la rama correcta |
| `BLOCKED_MODE_MISSING` | Falta MODO en la TaskSpec o prompt | Agregar MODO antes de ejecutar |
| `BLOCKED_MODE_INVALID` | MODO no es un valor válido | Corregir MODO |
| `BLOCKED_MODE_PHASE_CONFLICT` | MODO y FASE se contradicen | Revisar combinación |
| `BLOCKED_SCHEMA_INVALID` | TaskSpec no cumple schema | Corregir TaskSpec |
| `BLOCKED_SCOPE_EXPANSION` | NEXT_STEP intenta cambiar frente activo | Owner decide si acepta |
| `BLOCKED_TESTS_FAIL` | Tests no pasan | Corregir antes de cerrar |
| `IDLE` | No hay tareas pending | Estado válido; esperar nueva TaskSpec |

---

## 9. Formato de TaskSpec para este loop

Toda TaskSpec ejecutada por el TaskLoop soberano debe declarar:

```yaml
task_id: string
mode: create_only | patch_only | governance | product
operational_mode: ANALYSIS_ONLY | WRITE_AUTHORIZED | TEST_ONLY | CLOSE_ONLY | DOC_ONLY | BLOCKED_REVIEW
layer: string
phase: DEFINIR | CONTRATAR | IMPLEMENTAR | INTEGRAR | AUDITAR | CERRAR | DOCUMENTAR
model_target: CODEX | DEEPSEEK_4_PRO | DEEPSEEK_3_2
status: pending
objective: string
allowed_files: []
forbidden_files: []
required_tests: []
acceptance_criteria: []
preflight_commands: []
post_commands: []
```

Para prompts directos a Kiro, agregar:

```text
EJECUTOR: KIRO_LOCAL
```

`EJECUTOR` es metadato operativo. No va en el schema YAML.

---

## 10. Evidencia mínima por ciclo

```text
factory/evidence/<task_id>/
  cycle.md          → resumen del ciclo: tarea, ejecutor, resultado
  commands.txt      → comandos ejecutados
  git_status.txt    → estado del worktree antes y después
  git_diff.patch    → diff de archivos modificados
  tests.txt         → resultado de tests
  decision.txt      → veredicto y próximo paso
```

Sin evidencia verificable:

```text
NO_VALIDADO
```

---

## 11. Reglas de cierre de frente

Un frente activo se cierra cuando:

```text
1. Todas las TaskSpecs del frente tienen status=validated.
2. El gate está en APPROVED.
3. Existe evidencia de cierre en factory/evidence/.
4. El owner aprobó explícitamente el cierre.
5. Se creó el documento de cierre en docs/factory/.
```

Solo después del cierre formal se puede abrir un nuevo frente.

---

## 12. Próximo paso

```text
TS_030_003_INTEGRACION_CAPA_03
  MODO: ANALYSIS_ONLY
  EJECUTOR: KIRO_LOCAL (martes/jueves/sábado/domingo)
  Objetivo: auditar punto de integración de CaseOpeningService
            con OperationalCaseOrchestrator antes de conectar.
```
