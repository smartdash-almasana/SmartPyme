# TaskLoop IO Contract — SmartPyme Factory

## Estado

HITO 01 — Contrato de entradas y salidas soberanas del TaskLoop.

Este documento define cómo circula la información entre GPT Copiloto, Hermes, modelos ejecutores, GitHub y auditoría humana mínima.

Regla central:

```text
Toda tarea entra como JSON.
Toda ejecución sale como JSON.
Toda evidencia queda versionada.
Todo cierre produce decisión auditable.
```

---

## 1. Principio rector

SmartPyme Factory no debe depender de logs conversacionales ni de mensajes extensos por Telegram.

El ciclo operativo debe quedar representado por contratos de entrada/salida:

```text
TaskSpec JSON
→ ExecutionResult JSON
→ EvidenceManifest JSON
→ AuditDecision JSON
→ HumanEscalation JSON, solo si corresponde
```

El usuario no debe leer la ejecución interna. El usuario recibe solo cierre de hito o escalación humana real.

---

## 2. Roles del contrato

| Rol | Responsabilidad |
|---|---|
| GPT_COPILOTO_CHAT | Define frente activo, diseña TaskSpec, audita evidencia, decide si se informa al usuario |
| HERMES | Ejecuta en VM, corre TaskLoop, escribe evidencia, hace commit/push si está autorizado |
| DEEPSEEK_4_PRO | Auditoría o implementación acotada vía Hermes/OpenRouter |
| GEMINI_GOOGLE | Lectura larga, síntesis pesada, revisión conceptual de alto contexto |
| GPT_COPILOTO_GITHUB | Escritura directa controlada en GitHub cuando corresponde |
| KIRO_LOCAL | Ejecución local cómoda en días disponibles |
| USUARIO | Autoriza hitos, recibe buenas noticias o bloqueos humanos reales |

---

## 3. TaskSpec JSON

### Función

Define qué debe hacer la factoría en un ciclo único.

Una TaskSpec no es una conversación. Es una orden de trabajo acotada, auditable y ejecutable.

### Campos obligatorios V1

```json
{
  "task_id": "TS_FACTORY_001",
  "front_id": "FACTORIA",
  "layer": "FACTORY_PROTOCOL",
  "phase": "IMPLEMENTAR",
  "operational_mode": "WRITE_AUTHORIZED",
  "model_target": "DEEPSEEK_4_PRO",
  "provider_target": "OPENROUTER",
  "executor_target": "HERMES",
  "objective": "Implementar un cambio atómico y verificable.",
  "allowed_files": ["factory/core/queue_runner.py"],
  "forbidden_files": ["app/**", ".env", "config.yaml"],
  "preflight_commands": ["git status --short"],
  "validation_commands": ["python3 -m pytest tests/factory/test_queue_runner_sovereign.py -q"],
  "post_commands": ["git status --short"],
  "acceptance_criteria": ["Tests pasan", "Evidencia generada", "Gate queda en WAITING_AUDIT"],
  "status": "pending",
  "token_budget": {
    "max_prompt_tokens_est": 6000,
    "max_output_tokens_est": 3000,
    "max_files_read": 8,
    "max_searches": 5
  },
  "quiet_protocol": true,
  "human_required": false
}
```

### Estados permitidos

```text
pending
in_progress
done
blocked
failed
waiting_audit
```

### Modos permitidos

```text
ANALYSIS_ONLY
WRITE_AUTHORIZED
TEST_ONLY
CLOSE_ONLY
DOC_ONLY
BLOCKED_REVIEW
```

### Regla de scope

`allowed_files` no autoriza escritura por sí mismo.

Solo `operational_mode = WRITE_AUTHORIZED` o `DOC_ONLY` habilita escritura según alcance.

---

## 4. ExecutionResult JSON

### Función

Describe qué hizo realmente Hermes o el ejecutor durante el ciclo.

No reemplaza la evidencia. Resume la ejecución.

### Estructura V1

```json
{
  "task_id": "TS_FACTORY_001",
  "status": "done",
  "executor_real": "HERMES",
  "model_real": "DEEPSEEK_4_PRO",
  "provider_real": "OPENROUTER",
  "started_at": "2026-05-05T22:00:00Z",
  "finished_at": "2026-05-05T22:04:00Z",
  "commands_run": [
    {
      "command": "python3 -m pytest tests/factory/test_queue_runner_sovereign.py -q",
      "returncode": 0,
      "stdout_path": "factory/evidence/TS_FACTORY_001/tests.txt",
      "stderr_path": "factory/evidence/TS_FACTORY_001/tests.txt"
    }
  ],
  "files_changed": ["factory/core/queue_runner.py"],
  "commit_hash": "1899355",
  "push_status": "pushed",
  "blocking_reason": null
}
```

### Regla

Si `status != done`, debe existir `blocking_reason`.

---

## 5. EvidenceManifest JSON

### Función

Enumera la evidencia generada por el ciclo.

La evidencia vive en:

```text
factory/evidence/<task_id>/
```

### Estructura V1

```json
{
  "task_id": "TS_FACTORY_001",
  "evidence_dir": "factory/evidence/TS_FACTORY_001",
  "required_files": {
    "cycle": "factory/evidence/TS_FACTORY_001/cycle.md",
    "commands": "factory/evidence/TS_FACTORY_001/commands.txt",
    "git_status": "factory/evidence/TS_FACTORY_001/git_status.txt",
    "git_diff": "factory/evidence/TS_FACTORY_001/git_diff.patch",
    "tests": "factory/evidence/TS_FACTORY_001/tests.txt",
    "decision": "factory/evidence/TS_FACTORY_001/decision.txt"
  },
  "commit_hash": "1899355",
  "branch": "factory/ts-006-jobs-sovereign-persistence",
  "gate_status_after": "WAITING_AUDIT",
  "complete": true
}
```

### Regla

Si falta un archivo requerido, el ciclo no puede cerrarse como `done`.

---

## 6. AuditDecision JSON

### Función

Es la decisión de auditoría posterior al ciclo.

La puede emitir GPT_COPILOTO_CHAT tras leer GitHub/evidencia, o un auditor modelo si se lo invoca explícitamente.

### Estructura V1

```json
{
  "task_id": "TS_FACTORY_001",
  "decision": "PASS",
  "auditor": "GPT_COPILOTO_CHAT",
  "checked_commit": "1899355",
  "checked_evidence_dir": "factory/evidence/TS_FACTORY_001",
  "summary": "TaskLoop soberano V1 implementado y tests pasan.",
  "risks": [],
  "required_human_action": false,
  "next_gate_status": "OPEN",
  "next_milestone": "HITO_02"
}
```

### Decisiones permitidas

```text
PASS
PARTIAL
BLOCKED
REVERT_RECOMMENDED
HUMAN_REQUIRED
```

### Regla anti-deriva

`next_milestone` no cambia el `front_id` por recomendación automática de un agente.

Solo GPT_COPILOTO_CHAT o el usuario pueden cambiar el frente activo.

---

## 7. HumanEscalation JSON

### Función

Se emite solo cuando hace falta intervención humana real.

No se usa para logs, demoras normales ni dudas menores entre agentes.

### Estructura V1

```json
{
  "task_id": "TS_FACTORY_001",
  "escalation_type": "HUMAN_REQUIRED",
  "severity": "HIGH",
  "reason": "Se detectó posible secreto en archivo no versionado.",
  "decision_needed": "Rotar key o confirmar descarte del archivo.",
  "options": [
    "ROTATE_KEY",
    "DELETE_FILE_AND_CONTINUE",
    "STOP_FACTORY"
  ],
  "recommended_option": "ROTATE_KEY",
  "safe_to_continue": false
}
```

### Cuándo escalar al usuario

```text
- secreto/token/credencial detectada;
- riesgo de pérdida de datos;
- decisión económica o de negocio;
- cambio de infraestructura sensible;
- bloqueo que los agentes no pueden resolver;
- necesidad de autorización explícita.
```

### Cuándo no escalar

```text
- test falló y puede corregirse;
- falta un import;
- hay conflicto resoluble;
- se necesita reintentar un comando;
- hay que ajustar un prompt;
- hay que pedir auditoría a Gemini o DeepSeek.
```

---

## 8. Quiet Milestone Protocol

### Principio

El usuario no recibe logs ni seguimiento minuto a minuto.

Recibe solo cierres de hito.

### Mensajes permitidos al usuario

```text
HITO 01 DONE — contrato JSON I/O creado y versionado.
HITO 02 BLOCKED — falta autorización para tocar config Hermes.
HITO 03 HUMAN_REQUIRED — se detectó una key expuesta; requiere rotación.
HITO 04 REVERT_RECOMMENDED — el cambio rompe tests críticos.
```

### Mensajes prohibidos al usuario

```text
Estoy leyendo archivos...
Voy por la mitad...
Falló un test menor, pruebo otra cosa...
El agente tardó...
Hermes está pensando...
```

---

## 9. Control de modelos y tokens

### Regla general

La factoría debe elegir el modelo por tipo de tarea y presupuesto.

No se mandan tareas gigantes si pueden dividirse por capa/hito.

### Política V1

| Tipo de tarea | Modelo preferido | Límite operativo |
|---|---|---|
| Auditoría corta | DEEPSEEK_4_PRO | hasta 6k prompt estimado |
| Implementación acotada | DEEPSEEK_4_PRO o GPT_COPILOTO_GITHUB | máximo 3 archivos |
| Lectura larga/diseño pesado | GEMINI_GOOGLE | solo cuando DeepSeek no alcance |
| Refactor delicado | CODEX | solo si auth/provider operativo |
| Coordinación y auditoría final | GPT_COPILOTO_CHAT | sin ejecución de comandos |
| Escritura local | KIRO_LOCAL | solo días disponibles |

### TokenBudget JSON

```json
{
  "max_prompt_tokens_est": 6000,
  "max_output_tokens_est": 3000,
  "max_files_read": 8,
  "max_searches": 5,
  "split_required_if_exceeds": true
}
```

### Regla de partición

Si una tarea supera el presupuesto, debe dividirse en hitos:

```text
HITO_NA_ANALYSIS
HITO_NB_IMPLEMENTATION
HITO_NC_VALIDATION
```

---

## 10. Capa por capa

SmartPyme se construye capa por capa.

Una TaskSpec debe declarar `layer` y `phase`.

No se permite que una tarea de factoría derive a producto por recomendación automática.

Ejemplo:

```json
{
  "front_id": "FACTORIA",
  "layer": "FACTORY_PROTOCOL",
  "phase": "IMPLEMENTAR"
}
```

Si el agente propone avanzar a Capa 03 sin autorización:

```json
{
  "decision": "BLOCKED",
  "blocking_reason": "BLOCKED_SCOPE_DRIFT"
}
```

---

## 11. GitHub como realidad compartida

Hermes y GPT_COPILOTO_CHAT no comparten terminal.

Comparten GitHub.

```text
Hermes: pull → ejecuta → evidencia → commit/push
GPT: lee GitHub → audita diff/evidencia → decide cierre
```

Por eso todo resultado importante debe estar versionado o referenciado desde evidencia versionada.

---

## 12. Cierre de hito

Un hito se considera cerrado cuando existe:

```text
- ExecutionResult JSON o resumen equivalente;
- EvidenceManifest completo;
- commit_hash si hubo escritura;
- tests relevantes;
- AuditDecision PASS/PARTIAL/BLOCKED;
- gate en estado coherente.
```

El usuario recibe solo el estado del hito.

---

## 13. Próximos hitos sugeridos

```text
HITO 02 — Emitir EvidenceManifest JSON real desde queue_runner.
HITO 03 — Emitir ExecutionResult JSON real desde queue_runner.
HITO 04 — Agregar AuditDecision JSON como cierre de auditoría.
HITO 05 — Formalizar HumanEscalation JSON y Quiet Milestone Protocol en AGENT_WORKFLOW.md.
```

---

## 14. Frase rectora

```text
Menos chat. Más contratos.
Menos logs al usuario. Más evidencia versionada.
Menos tareas gigantes. Más hitos cerrados.
```
