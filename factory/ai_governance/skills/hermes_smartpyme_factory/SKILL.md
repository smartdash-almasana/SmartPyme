---
name: hermes_smartpyme_factory
description: Ejecuta ciclos SmartPyme Factory con Hermes, delegation, evidencia, git y maximo tres agentes.
version: 1.1.0
platforms: [linux]
metadata:
  hermes:
    category: devops
    tags: [smartpyme, factory, multiagent, governance, hallazgos, hermes]
---

# Hermes SmartPyme Factory

## Activador

Cuando el usuario diga:

```text
Ejecuta un ciclo SmartPyme Factory
```

Hermes debe ejecutar UN ciclo completo sobre un unico hallazgo pending.

## Modelo

- Hermes = orquestador.
- Gemini 2.5 = modelo activo de Hermes.
- SmartPyme repo = fuente de verdad.
- Hallazgo markdown = unidad de trabajo.
- GitHub = persistencia.
- Evidencia = condicion de cierre.

## Workspaces validos

Hermes puede operar solo si `pwd` es uno de estos:

```text
/home/neoalmasana/smartpyme-factory/repos/SmartPyme
/opt/smartpyme-factory/repos/SmartPyme
```

Precheck obligatorio:

```bash
pwd
git remote -v
git status --short
git log --oneline -1
```

Remote obligatorio:

```text
https://github.com/smartdash-almasana/SmartPyme.git
```

Si falla: `BLOCKED_WRONG_WORKSPACE`.

## Toolsets requeridos

Hermes debe operar con:

```text
terminal
file
skills
delegation
todo
```

## Maximo tres agentes

1. Architect/Planner: convierte hallazgo en plan y alcance.
2. Builder: ejecuta cambios permitidos.
3. Auditor: valida evidencia sin modificar archivos.

Hermes no debe crear mas de tres subagentes para un ciclo.

## Estados

```text
factory/hallazgos/pending
factory/hallazgos/in_progress
factory/hallazgos/done
factory/hallazgos/blocked
```

Flujo:

```text
pending -> in_progress -> done | blocked
```

## Ciclo autonomo

1. Si el repo esta limpio: ejecutar `git pull --rebase origin main`.
2. Leer `factory/hallazgos/pending/*.md`.
3. Si no hay pending: responder `status=idle`.
4. Seleccionar un solo hallazgo.
5. Validar que tenga objetivo, rutas, restricciones, criterios y validaciones.
6. Moverlo a `in_progress`.
7. Delegar a Builder con toolsets `terminal,file`.
8. Builder modifica solo rutas autorizadas y genera evidencia.
9. Delegar a Auditor con toolsets `terminal,file`.
10. Auditor responde `VALIDADO` o `NO_VALIDADO`.
11. Hermes mueve a `done` o `blocked`.
12. Hermes escribe evidencia final.
13. Hermes hace commit y push solo si el cierre es consistente.

## Evidencia obligatoria

Para cada hallazgo:

```text
factory/evidence/<hallazgo_id>/builder_report.md
factory/evidence/<hallazgo_id>/auditor_report.md
factory/evidence/<hallazgo_id>/git_status.txt
factory/evidence/<hallazgo_id>/diff.patch
factory/evidence/<hallazgo_id>/status.json
```

Sin evidencia verificable: `NO_VALIDADO` y estado `blocked`.

## Reglas de desarrollo SmartPyme

Antes de codigo de producto, Architect y Builder deben respetar:

```text
docs/specs/01-arquitectura.md
docs/specs/02-data-model.md
docs/specs/04-pipeline.md
docs/guias/protocolo-write-verify-run.md
docs/guias/reglas-ia.md
```

Si no existen o no pueden leerse: `NO_VALIDADO`.

Capas obligatorias:

```text
contracts -> repositories -> services -> core/pipeline -> adapters
```

Prohibido saltar capas, mezclar tenants o acceder DB sin repository.

## Verdad de negocio

Hermes no decide la verdad. SmartPyme valida.

Regla:

```text
verdad = evidencia + formula + criterio humano + contexto temporal
```

Si falta tenant_id, evidencia, formula o criterio requerido: `BLOCKED` o `CLARIFY`.

## Prohibiciones

- Builder no audita.
- Auditor no corrige.
- Hermes no valida su propio trabajo.
- No tocar `app/**`, `core/**`, `services/**` o tests sin hallazgo explicito.
- No inventar datos.
- No responder sin evidencia cuando sea dato de negocio.

## Salida final de ciclo

Hermes debe responder:

```text
VEREDICTO_CICLO: done | blocked | idle
HALLAZGO:
AGENTES_USADOS:
ARCHIVOS_TOCADOS:
EVIDENCIA:
TESTS:
COMMIT:
PUSH:
RIESGOS:
```
