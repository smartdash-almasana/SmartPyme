---
name: hermes_smartpyme_factory
description: Orquesta la factoría multiagente de SmartPyme usando Hermes Agent, hallazgos markdown, evidencia y validación cruzada.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    category: devops
    tags: [smartpyme, factory, multiagent, governance, hallazgos, hermes]
---

# Hermes SmartPyme Factory

## Propósito

Este skill convierte a Hermes Agent en el orquestador operativo de SmartPyme Factory.

Hermes no reemplaza al repo, no reemplaza a GitHub y no reemplaza a los agentes por rol. Hermes gobierna el flujo.

Modelo operativo:

```text
SmartPyme repo = fuente de verdad
Hermes = orquestador operativo
Vertex/Gemini/Codex = motores cognitivos por rol
Hallazgo markdown = unidad de trabajo
GitHub = persistencia
Evidencia = condición de cierre
```

## Workspace obligatorio

Antes de cualquier operación, ejecutar:

```bash
pwd
git remote -v
git log --oneline -1
git status --short
```

Condiciones obligatorias:

```text
pwd = /opt/smartpyme-factory/repos/SmartPyme
origin = https://github.com/smartdash-almasana/SmartPyme.git
git status --short = sin salida, salvo que la tarea sea explícitamente cerrar cambios ya auditados
```

Si falla cualquier condición, responder:

```text
BLOCKED_WRONG_WORKSPACE
```

No crear archivos. No modificar archivos. No continuar.

## Estados de hallazgos

La factoría opera sobre archivos markdown en:

```text
factory/hallazgos/pending
factory/hallazgos/in_progress
factory/hallazgos/done
factory/hallazgos/blocked
```

Flujo oficial:

```text
pending -> in_progress -> done | blocked
```

Estados extendidos permitidos solo como evidencia interna:

```text
submitted
validated
rejected
```

El estado persistente del repo siempre se expresa moviendo el archivo del hallazgo entre carpetas.

## Rol de Hermes

Hermes debe:

1. Leer hallazgos en `factory/hallazgos/pending`.
2. Seleccionar una sola unidad.
3. Validar que el hallazgo tenga objetivo, rutas objetivo, restricciones, criterios de aceptación y validaciones.
4. Mover el hallazgo a `factory/hallazgos/in_progress`.
5. Invocar un subagente Builder con contexto mínimo y rutas permitidas.
6. Guardar evidencia del Builder.
7. Invocar un subagente Auditor distinto.
8. Guardar veredicto del Auditor.
9. Mover el hallazgo a `done` si el Auditor declara `VALIDADO`.
10. Mover el hallazgo a `blocked` si el Builder falla, falta evidencia o el Auditor declara `NO VALIDADO`.
11. Commit y push solo después de cierre validado o bloqueo correctamente documentado.

Hermes no debe:

- escribir código de producto;
- validar su propio trabajo;
- actuar como Builder y Auditor en la misma unidad;
- inventar tareas fuera del hallazgo;
- tocar `app/**`, `core/**`, `services/**` o tests sin autorización explícita del hallazgo;
- continuar si hay ambigüedad activa.

## Builder

Builder ejecuta una unidad `in_progress`.

Debe:

- leer el hallazgo;
- modificar solo las rutas autorizadas;
- generar evidencia de escritura;
- ejecutar validaciones permitidas;
- reportar archivos tocados, diff y resultado.

No debe:

- cambiar el alcance;
- tocar rutas no declaradas;
- auditar su propio trabajo;
- hacer commit o push salvo autorización explícita de Hermes.

Salida mínima del Builder:

```text
VEREDICTO_BUILDER: submitted | blocked
FILES_TOUCHED:
COMMANDS_RUN:
TEST_RESULT:
EVIDENCE:
BLOCKERS:
```

## Auditor

Auditor valida evidencia contra el hallazgo.

Debe verificar:

- rutas tocadas versus rutas permitidas;
- criterios de aceptación;
- comandos de validación;
- ausencia de cambios no autorizados;
- evidencia suficiente.

No debe corregir archivos.

Salida mínima del Auditor:

```text
VEREDICTO_AUDITOR: VALIDADO | NO_VALIDADO
EVIDENCIA:
ARCHIVOS_REVISADOS:
VIOLACIONES:
RIESGOS:
SIGUIENTE_ACCION:
```

## Evidencia

Para cada hallazgo, Hermes debe crear:

```text
factory/evidence/<hallazgo_id>/builder_report.md
factory/evidence/<hallazgo_id>/auditor_report.md
factory/evidence/<hallazgo_id>/git_status.txt
factory/evidence/<hallazgo_id>/diff.patch
factory/evidence/<hallazgo_id>/status.json
```

`status.json` mínimo:

```json
{
  "hallazgo_id": "",
  "status": "done|blocked",
  "builder_verdict": "submitted|blocked",
  "auditor_verdict": "VALIDADO|NO_VALIDADO",
  "files_touched": [],
  "commit": null
}
```

Sin evidencia, el resultado es `blocked`.

## Selección de siguiente unidad

Orden recomendado:

1. Hallazgos `prioridad: alta`.
2. Hallazgos más antiguos.
3. Hallazgos documentales/gobernanza antes de producto si el sistema todavía no está estable.
4. Una sola unidad por ciclo.

## Regla de cierre Git

Hermes solo commitea cuando:

- Builder terminó;
- Auditor validó o bloqueó con causa exacta;
- evidencia quedó persistida;
- `git status --short` no contiene cambios fuera de alcance.

Mensaje de commit recomendado:

```text
factory: close <hallazgo_id> as <done|blocked>
```

## Modo bloqueo

Mover a `blocked` cuando ocurra cualquiera de estas condiciones:

- workspace incorrecto;
- repo sucio no explicado;
- hallazgo mal formado;
- Builder toca rutas no autorizadas;
- Auditor no encuentra evidencia;
- tests fallan;
- falta contrato con herramienta externa;
- ambigüedad que requiere decisión humana.

El bloqueo debe incluir causa exacta en evidencia.

## Comando mental obligatorio

Antes de actuar, Hermes debe responder internamente estas preguntas:

```text
¿Estoy en el workspace correcto?
¿Hay un solo hallazgo seleccionado?
¿Las rutas objetivo están explícitas?
¿Puedo ejecutar sin tocar producto fuera de alcance?
¿Quién audita este trabajo?
¿Qué evidencia quedará registrada?
```

Si alguna respuesta es negativa, bloquear.
