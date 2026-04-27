# MCP Surfaces — SmartPyme Factory

Hermes puede usar MCP como capa de herramientas controladas.

## Superficies

- filesystem: limitado al repo SmartPyme.
- git: status, diff, add, commit, pull, push.
- github: lectura remota, commits, archivos, issues o hallazgos.
- codex: Builder opcional para codigo cuando haya tokens.

## Regla

MCP no decide estados. Hermes orquesta. Auditor valida. GitHub persiste.

## Prohibido

- force push
- secretos
- rutas fuera del repo
- cambios sin hallazgo
- Builder auditando su propio trabajo
