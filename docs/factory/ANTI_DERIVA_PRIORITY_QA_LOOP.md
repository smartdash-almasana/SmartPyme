# ANTI-DERIVA + PRIORITY + QA LOOP — SmartPyme Factory

## Estado
CANONICO v1

## Objetivo
Diseñar el circuito permanente que impide deriva, revisa prioridades despues de cada avance y ejecuta QA/auditoria perpetua sobre la factoría SmartPyme.

---

## 1. Principio rector

La factoría no puede limitarse a ejecutar tareas.
Debe ejecutar, auditar, reordenar prioridades y corregir dirección en cada ciclo.

Ciclo canonico:

```text
PLANIFICAR → EJECUTAR → VALIDAR → AUDITAR → DOCUMENTAR → REPRIORIZAR → SIGUIENTE CICLO
```

---

## 2. Tres procesos sincronizados

### A. Anti-deriva
Evita que los agentes:
- inventen arquitectura
- creen formatos paralelos
- salten contratos canonicos
- trabajen fuera del objetivo actual
- optimicen tareas irrelevantes

### B. Repriorizacion continua
Despues de cada ciclo revisa:
- que se construyo
- que quedo bloqueado
- que dependencia se desbloqueo
- que item sube o baja prioridad
- que nueva idea debe entrar a TECH_SPEC_QUEUE

### C. QA perpetuo
Audita:
- calidad tecnica
- cumplimiento de contrato
- evidencia real
- tests
- trazabilidad
- coherencia con SmartPyme Core

---

## 3. Roles por agente

### Hermes
Responsable de orquestar el ciclo completo.

Debe:
- leer tasks, hallazgos, roadmap y TECH_SPEC_QUEUE
- elegir una sola unidad de trabajo
- despachar a Gemini o Codex segun corresponda
- exigir evidencia
- bloquear cierres invalidos
- ejecutar repriorizacion post-ciclo

### Gemini
Responsable de razonamiento, arquitectura y auditoria semantica.

Debe:
- detectar deriva conceptual
- verificar coherencia con contratos canonicos
- proponer prioridades
- convertir ideas nuevas en specs
- auditar outputs de Codex cuando toquen arquitectura o negocio

### Codex
Responsable de construccion tecnica.

Debe:
- implementar cambios pequenos
- escribir tests
- ejecutar validaciones
- dejar diff y evidencia
- no redefinir arquitectura sin spec previa

---

## 4. Guardrails anti-deriva

Un ciclo queda BLOCKED si ocurre cualquiera de estos casos:

1. El cambio no referencia task, hallazgo o spec.
2. El output crea contrato nuevo sin actualizar specs canonicas.
3. Se genera hallazgo sin entidad, diferencia y fuentes.
4. Codex modifica core sin test.
5. Gemini propone arquitectura sin registrar spec.
6. Hermes no puede explicar por que eligio esa tarea.
7. Hay cambios sin evidencia.
8. La tarea no actualiza estado final.

---

## 5. Sistema de prioridades v1

Cada item debe tener score:

```yaml
priority_score:
  business_impact: 1-5
  technical_leverage: 1-5
  unblock_value: 1-5
  implementation_risk: 1-5
  urgency: 1-5
```

Formula inicial:

```text
score = business_impact + technical_leverage + unblock_value + urgency - implementation_risk
```

Reglas:
- mayor score = mayor prioridad
- bloqueos de arquitectura suben prioridad
- tareas sin contrato bajan prioridad
- tareas de core deterministico tienen prioridad sobre integraciones ornamentales

---

## 6. Estado obligatorio de cada item

```yaml
item_state:
  id: string
  source: TECH_SPEC_QUEUE | TASK | HALLAZGO | ROADMAP
  status: proposed | pending | in_progress | blocked | done | archived
  priority_score: integer
  last_cycle_result: CORRECTO | BLOCKED | NO_VALIDADO | IDLE
  evidence_path: string | null
  next_action: string | null
```

---

## 7. Auditoria post-ciclo

Al terminar cada ciclo, debe generarse:

```text
factory/evidence/<cycle_id>/qa_report.md
factory/evidence/<cycle_id>/priority_update.md
factory/evidence/<cycle_id>/anti_deriva_check.md
```

Contenido minimo de `qa_report.md`:
- tarea ejecutada
- archivos tocados
- tests corridos
- evidencia
- decision
- riesgos

Contenido minimo de `priority_update.md`:
- prioridad antes
- prioridad despues
- motivo del cambio
- nuevos items detectados
- items promovidos a task

Contenido minimo de `anti_deriva_check.md`:
- contratos revisados
- desviaciones detectadas
- estado: PASS | WARNING | BLOCKED

---

## 8. Contratos canonicos que deben revisarse

- `docs/specs/CORE_DATA_CONTRACT_AND_HALLAZGOS.md`
- `docs/factory/HERMES_CODEX_GEMINI_GOVERNANCE.md`
- `docs/factory/TECH_SPEC_QUEUE.md`
- `AGENTS.md`
- `CODEX.md`
- `GEMINI.md`

---

## 9. Cierre de ciclo valido

Un ciclo solo puede cerrarse como CORRECTO si:

1. Tiene task o item origen.
2. Tiene evidencia.
3. Tiene verificacion fisica.
4. Tiene QA post-ciclo.
5. Tiene anti_deriva_check.
6. Tiene priority_update.
7. Si toca codigo, tiene test.
8. Si toca arquitectura, Gemini audita coherencia.

---

## 10. Proxima implementacion requerida

Crear task:

```yaml
task_id: anti-deriva-priority-qa-loop-v1
status: pending
objetivo: Implementar el loop de control post-ciclo que genere QA, anti-deriva y repriorizacion.
```

---

## 11. Resultado esperado

La factoría debe pasar de:

```text
ejecutar tareas
```

a:

```text
ejecutar tareas + auditar calidad + corregir direccion + repriorizar backlog
```
