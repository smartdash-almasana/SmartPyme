# Hermes Skills Integration — SmartPyme Factory

Estado: CANONICO v1  
Remediacion: P0-4 — documentar gap de carga real de skills Hermes  
Fecha: 2026-04-28

## Objetivo

Cerrar la contradiccion P0-4: SmartPyme versiona skills en el repo, pero debe existir evidencia operativa de que Hermes Gateway realmente las carga.

Este documento no activa Hermes, no modifica configuracion local y no crea runtime. Solo define el contrato de verificacion.

## Fuente versionada

Las skills SmartPyme versionadas viven en:

```text
factory/ai_governance/skills/
```

Skill principal auditada:

```text
factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md
```

## Gap operativo

Hermes Gateway puede operar solo si la skill versionada es visible para Hermes en la configuracion real de la VM.

Hasta que exista evidencia, el estado es:

```text
HERMES_SKILLS_NOT_VERIFIED
```

No se debe declarar que Hermes puede ejecutar SmartPyme Factory por skills hasta probar una de las opciones de integracion.

## Opcion A — instalar/copiar skills al directorio Hermes

Copiar o sincronizar las skills versionadas del repo hacia el directorio local de Hermes en la VM.

Uso esperado:

```text
repo SmartPyme -> ~/.hermes/skills/
```

Requisito:

- debe existir comando reproducible;
- debe quedar evidencia de `ls` o equivalente;
- debe probarse que Hermes las lista o las reconoce.

## Opcion B — configurar external_dirs en Hermes

Declarar el directorio versionado de skills de SmartPyme en la configuracion local de Hermes.

Uso esperado:

```text
~/.hermes/config.yaml -> skills.external_dirs -> /opt/smartpyme-factory/repos/SmartPyme/factory/ai_governance/skills
```

Requisito:

- no versionar secretos;
- no tocar tokens;
- respaldar config local antes de modificarla;
- probar que Hermes reconoce la skill tras reinicio o reload.

## Criterio de aceptacion P0-4

P0-4 solo queda cerrado si existe evidencia de:

1. ruta real del repo SmartPyme en VM;
2. ruta real de config Hermes en VM;
3. metodo elegido: Opcion A u Opcion B;
4. skill `hermes_smartpyme_factory` visible para Hermes;
5. prueba de no ejecucion de runners legacy;
6. evidencia guardada en `factory/evidence/TASK-HERMES-SKILLS-VERIFY-001/`.

## Bloqueos

Si no se puede comprobar que Hermes carga la skill, responder:

```text
BLOCKED_HERMES_SKILLS_NOT_VERIFIED
```

Si se detecta dependencia de runner legacy, responder:

```text
BLOCKED_LEGACY_RUNTIME_CONTAMINATION
```

## Validacion recomendada

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && git pull --ff-only origin main

test -f factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md

grep -n "hermes_smartpyme_factory\|external_dirs\|quick_commands" /home/neoalmasana/.hermes/config.yaml || true

ps -ef | grep -E "hermes_factory_runner|telegram_factory_control" | grep -v grep || true
```

El ultimo comando debe devolver vacio para considerar que no hay runtime legacy activo.
