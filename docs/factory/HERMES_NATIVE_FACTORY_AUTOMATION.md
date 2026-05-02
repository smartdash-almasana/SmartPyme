# Hermes Native Factory Automation — SmartPyme Factory

Estado: CANONICO v1
Fecha: 2026-05-02

## Proposito

Este documento define como SmartPyme Factory debe usar la sistematica nativa de Hermes para automatizar practicas de desarrollo sin crear runners paralelos ni flujos improvisados.

## Fuentes revisadas

Hermes:

- `website/docs/user-guide/configuration.md`
- `website/docs/developer-guide/creating-skills.md`
- `website/docs/user-guide/features/tools.md`
- `website/docs/user-guide/features/code-execution.md`

SmartPyme:

- `docs/factory/FACTORY_CONTRATO_OPERATIVO.md`
- `docs/factory/HERMES_SKILLS_INTEGRATION.md`
- `docs/factory/AI_PROVIDER_ROUTING_CONTRACT.md`
- `docs/SKILLS_CATALOGO_SMARTPYME.md`
- `factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md`

## Verdad operativa

```text
Telegram -> Hermes Gateway -> quick commands / skills -> Repo -> Tests -> Evidencia -> Auditoria -> Decision humana
```

Hermes Gateway es el runtime conversacional. SmartPyme repo es la fuente versionada. TaskSpec YAML es la unidad de trabajo.

## Skills nativas Hermes

Hermes recomienda usar una Skill cuando una capacidad puede expresarse como instrucciones, comandos shell y herramientas existentes.

Para SmartPyme Factory aplica a:

- avanzar un ciclo;
- auditar estado;
- validar tests y ruff;
- registrar evidencia;
- preparar reporte final;
- detectar contaminacion legacy.

Una Tool corresponde solo cuando hace falta integracion precisa o logica custom que debe ejecutarse igual cada vez.

## Formato de Skill

Toda skill real debe seguir el patron `SKILL.md`:

```markdown
---
name: smartpyme-development-automation
description: Automatiza validaciones de desarrollo para SmartPyme Factory.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [smartpyme, factory, development, validation]
---

# Skill Title

## When to Use
## Quick Reference
## Procedure
## Pitfalls
## Verification
```

La skill rectora actual es:

```text
factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md
```

## Ubicacion recomendada

No corresponde inventar un contrato aislado si la practica pertenece al flujo operativo de Hermes.

Ubicacion principal:

```text
factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md
```

Si la practica crece como capacidad separada:

```text
factory/ai_governance/skills/smartpyme_development_automation/SKILL.md
```

Luego debe verificarse que Hermes Gateway realmente carga esa skill.

## Toolsets relevantes

Para la factoria importan:

```text
terminal
file
skills
todo
cronjob
code_execution
delegation
clarify
mcp-<server>
```

Uso esperado:

```text
terminal -> comandos shell, tests, ruff, git, builds
execute_code -> workflows con multiples herramientas y procesamiento Python
cronjob -> tareas programadas no destructivas
skills -> procedimientos versionados
clarify -> consulta cuando hay ambiguedad
delegation -> subtareas si el flujo lo permite
```

## Terminal vs execute_code

Usar `terminal` para:

```text
pytest
ruff
git status
git diff
git commit
git push
procesos de gateway
```

Usar `execute_code` para:

```text
analizar muchos archivos con logica intermedia
filtrar resultados masivos
resumir outputs antes de devolverlos al modelo
workflows multi-step con herramientas Hermes y procesamiento Python
```

No usar `execute_code` para builds o tests simples.

## Rutinas y jobs programados

Hermes documenta capacidades programadas bajo `cronjob` y directorios locales de cron. No se debe asumir una capa separada llamada routines salvo evidencia en la version instalada.

Uso permitido:

- health checks;
- refrescos operativos;
- reportes periodicos;
- verificaciones no destructivas.

Uso prohibido:

- ejecutar patches automaticos sin TaskSpec;
- modificar codigo productivo sin gate;
- reactivar runners legacy.

## Ciclo de desarrollo automatizado minimo

Toda TaskSpec que toque Python debe cerrar con:

```text
1. git status inicial
2. validacion de allowed_files / forbidden_files
3. patch minimo
4. pytest especifico sobre tests relevantes
5. ruff sobre archivos tocados
6. git diff resumido
7. evidencia en factory/evidence/<task_id>/
8. commit
9. push
10. reporte final
```

Reporte final obligatorio:

```text
VEREDICTO
ARCHIVOS_MODIFICADOS
TESTS_RUN
RUFF_RUN
GIT_STATUS
COMMIT_SHA
PUSH_STATUS
NEXT
```

Si falta `TESTS_RUN` o `RUFF_RUN` en una tarea Python, el Auditor debe bloquear o devolver `NEEDS_REVIEW`.

## Frecuencia de validacion

Patch Python chico:

```text
pytest sobre tests especificos
ruff check sobre archivos tocados
```

Patch Python importante:

```text
pytest relevante
ruff check app tests
```

Antes de merge/main:

```text
suite completa
ruff check app tests
```

## Gate de duda

Cuando Hermes no puede determinar alcance, tests requeridos, impacto o archivo correcto, debe consultar. No debe llenar el repo con documentos o parches especulativos.

Veredicto:

```text
BLOCKED_NEEDS_OWNER_DECISION
```

Debe incluir:

```text
motivo exacto
opciones minimas
recomendacion unica
```

## Auditoria de estado actual

Estado observado:

```text
docs/SKILLS_CATALOGO_SMARTPYME.md declara skills conceptuales y algunas parciales.
factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md define el ciclo operativo vigente.
docs/factory/HERMES_SKILLS_INTEGRATION.md exige verificar que Hermes Gateway carga realmente la skill.
```

Conclusion:

```text
No alcanza con versionar skills en el repo. Debe existir evidencia de que Hermes las ve y las carga.
```

## Recomendacion operativa

Evolucion recomendada:

```text
Fase 1 - Documentar validaciones dentro de hermes_smartpyme_factory/SKILL.md
Fase 2 - Verificar carga real de skill en Hermes Gateway
Fase 3 - Agregar validacion obligatoria al ciclo /avanzar
Fase 4 - Auditor bloquea si falta TESTS_RUN, RUFF_RUN o evidencia
Fase 5 - Solo despues crear scripts auxiliares si la skill queda demasiado larga
```

No modificar `factory/core/task_spec_runner.py` sin TaskSpec especifica y evidencia de que esa es la integracion correcta.
