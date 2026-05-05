# FACTORY OPERATING SNAPSHOT — HITO 08B

**Fecha de congelación:** 2026-05-05  
**Límite de validez:** Hasta que se modifique el runtime de factoría (queue_runner, task_loop, task_spec, task_spec_store).  
**Propósito:** Los próximos ciclos de factoría no deben redescubrir el flujo; pueden basarse en este snapshot para ejecutar sin re‑leer arquitectura base.

---

## 1. ENTRYPOINT OFICIAL

```bash
python3 -m factory.core.run_taskloop_once --mode sovereign
```

Este comando devuelve un objeto JSON compacto con el resultado del ciclo. Variantes:

```bash
# Override paths
python3 -m factory.core.run_taskloop_once --mode sovereign \
    --tasks-dir factory/taskspecs \
    --evidence-dir factory/evidence/taskspecs \
    --gate-path factory/control/AUDIT_GATE.md \
    --repo-root .
```

**`--mode`** acepta `sovereign` (default) o `multiagent`. Solo `sovereign` se usa en producción actual.

---

## 2. RUTAS OFICIALES (defaults)

| Ruta | Propósito |
|------|-----------|
| `factory/taskspecs` | Directorio raíz de TaskSpecs (JSON) |
| `factory/evidence/taskspecs` | Directorio base para evidencia de cada TaskSpec |
| `factory/control/AUDIT_GATE.md` | Archivo de control que indica si la factoría puede ejecutar |

El ciclo soberano respeta estas rutas por defecto; se pueden sobreescribir por CLI.

---

## 3. FUNCIÓN INTERNA INVOCADA

```python
from factory.core.queue_runner import run_one_queued_task

result = run_one_queued_task(
    tasks_dir="factory/taskspecs",
    evidence_dir="factory/evidence/taskspecs",
    use_sovereign=True,
    gate_path="factory/control/AUDIT_GATE.md",
    repo_root=".",
)
```

- `use_sovereign=True` activa el flujo soberano (gate, TaskSpecStore, evidencia mínima).
- El ciclo normal solo debe conocer **esta firma**; no necesita re‑leer `queue_runner.py`, `task_spec.py`, `task_spec_store.py`, `task_loop.py` ni tests base.

---

## 4. QUÉ LEE UN CICLO NORMAL

1. **TaskSpec pendiente** – desde `factory/taskspecs/pending/` (por TaskSpecStore).
2. **Gate status** – línea `status:` del archivo `factory/control/AUDIT_GATE.md`.
3. **Snapshot operativo** – este documento (solo si se requiere contexto de contexto; no de runtime).

**No debe releer:**  
- Código de `factory/core/` (queue_runner, task_spec, task_spec_store, task_loop).  
- Tests (`tests/factory/`).  
- Arquitectura base (diseños, contratos, documentación de flujo).

---

## 5. EVIDENCIA OBLIGATORIA POR CICLO

Cada ciclo genera un directorio `factory/evidence/taskspecs/<task_id>/` con estos archivos:

| Archivo | Contenido mínimo |
|---------|------------------|
| `cycle.md` | Resumen del ciclo (task_id, status, operational_mode, gate_status_start, blocking_reason) |
| `commands.txt` | Salida de los comandos ejecutados (stdout + stderr) |
| `git_status.txt` | `git status --short` al inicio del ciclo |
| `git_diff.patch` | `git diff --no-color HEAD` al inicio del ciclo |
| `tests.txt` | Salida de los tests de validación (si los hay) |
| `decision.txt` | Decisión final (status, blocking_reason) |
| `execution_result.json` | JSON con detalles de ejecución (comandos, cambios, commit_hash, etc.) |
| `evidence_manifest.json` | Manifiesto de evidencia generada (lista de archivos, commit_hash, gate_status_after) |
| `audit_decision.json` | Decisión de auditoría (emitida por GPT_COPILOTO_CHAT o auditor modelo) |
| `human_escalation.json` | Solo si se requiere escalación humana real (secreto, riesgo, decisión económica) |

**Regla:** Si falta un archivo del conjunto mínimo (`cycle.md`, `commands.txt`, `git_status.txt`, `git_diff.patch`, `tests.txt`, `decision.txt`), el ciclo no puede cerrarse como `done`.

---

## 6. SALIDA MÍNIMA ESPERADA (JSON)

El entrypoint devuelve un objeto JSON con los siguientes campos:

```json
{
  "status": "done" | "blocked" | "idle" | "in_progress",
  "task_id": "string | null",
  "evidence_dir": "ruta/al/directorio/evidence",
  "evidence_manifest_path": "ruta/al/evidence_manifest.json",
  "execution_result_path": "ruta/al/execution_result.json",
  "audit_decision_path": "ruta/al/audit_decision.json",
  "human_escalation_path": "ruta/al/human_escalation.json | null",
  "blocking_reason": "string | null",
  "gate_status": "OPEN | CLOSED | WAITING_AUDIT | ..."
}
```

- `status`: estado final del ciclo.
- `task_id`: identificador de la TaskSpec procesada (o `null` si no hubo tarea pendiente).
- `evidence_dir`: directorio donde se almacenó toda la evidencia.
- `evidence_manifest_path`: ruta al manifiesto de evidencia.
- `execution_result_path`: ruta al resultado de ejecución.
- `audit_decision_path`: ruta a la decisión de auditoría.
- `human_escalation_path`: ruta a la escalación humana (solo si existe).
- `blocking_reason`: motivo de bloqueo (si `status` es `blocked`).
- `gate_status`: estado del gate después del ciclo.

---

## 7. REGLA ANTI‑LABERINTO

> “Si el hito **no modifica el runtime de factoría**, no auditar arquitectura base.”

Esta regla evita ciclos de redescubrimiento innecesarios.  
Cuando un hito solo afecta documentación, configuración o evidencia, el ciclo debe:

1. Leer este snapshot para conocer el flujo operativo.
2. Ejecutar solo los comandos de validación definidos en la TaskSpec.
3. Generar la evidencia obligatoria.
4. No revisar `queue_runner.py`, `task_spec.py`, `task_spec_store.py`, `task_loop.py` ni sus tests.

Excepción: si la TaskSpec pide explícitamente “auditar arquitectura base”, se debe hacer una revisión acotada y documentar por qué fue necesaria.

---

## 8. EJEMPLO DE CICLO ESTÁNDAR

```bash
# 1. Verificar gate
cat factory/control/AUDIT_GATE.md | grep "status:"

# 2. Ejecutar un ciclo
python3 -m factory.core.run_taskloop_once --mode sovereign --compact

# Salida esperada (ejemplo):
# {
#   "status": "done",
#   "task_id": "TS_FACTORY_001",
#   "evidence_dir": "factory/evidence/taskspecs/TS_FACTORY_001",
#   ...
# }
```

---

## 9. ESTADOS DE GATE PERMITIDOS

| Estado | Significado |
|--------|-------------|
| `OPEN` | La factoría puede ejecutar. |
| `APPROVED` | Auditoría aprobó ejecución (equivalente a OPEN). |
| `RUN` | Equivalente a OPEN. |
| `WAITING_AUDIT` | Ciclo terminó, esperando auditoría. |
| `CLOSED` | La factoría no debe ejecutar. |
| `MISSING` | No existe archivo de gate. |

El ciclo soberano bloquea si el gate no está en `OPEN`, `APPROVED` o `RUN`.

---

## 10. QUÉ HACER CON ESTE SNAPSHOT

- **Si el hito modifica runtime de factoría** → actualizar este documento después del cambio.
- **Si el hito no modifica runtime** → usar este snapshot como fuente única de verdad operativa.
- **Si detectas inconsistencia** entre snapshot y realidad → escalar como `HUMAN_REQUIRED` (archivo `human_escalation.json`).

---

**Última revisión de coherencia:** 2026‑05‑05 (queue_runner.py v1.0, run_taskloop_once.py v1.0, TASK_LOOP_IO_CONTRACT.md HITO 01).