# ROUTES CONTRACT — SmartPyme Factory

## Estado

CANONICO OPERATIVO v1.0.

Este documento es la fuente de verdad para rutas operativas de SmartPyme Factory, Hermes Agent y Hermes Runtime en la VM `smartpyme-factory`.

Su objetivo es eliminar ambigüedad entre rutas reales, rutas históricas, Cloud Shell, workspace Docker y documentación interna del repo.

---

## 1. Rutas canónicas vigentes

### 1.1 Repo SmartPyme en VM

```text
/opt/smartpyme-factory/repos/SmartPyme
```

Uso:

- código producto SmartPyme;
- ejecución de tests;
- ejecución de Ruff;
- lectura de `GPT.md`, `AGENTS.md`, `GEMINI.md`, `CODEX.md`, `HERMES.md`;
- operación de TaskSpecs y factory loop;
- destino de `git pull` desde GitHub.

Regla:

```text
Toda operación sobre código SmartPyme debe ejecutarse desde /opt/smartpyme-factory/repos/SmartPyme.
```

---

### 1.2 Repo Hermes Agent externo

```text
/opt/smartpyme-factory/repos/hermes-agent
```

Uso:

- código fuente externo del orquestador Hermes Agent;
- gateway, CLI, runtime multiagente;
- dependencias internas de Hermes.

Regla:

```text
No tratar /opt/smartpyme-factory/repos/hermes-agent como código producto SmartPyme.
```

---

### 1.3 Runtime/configuración Hermes

```text
/home/neoalmasana/.hermes/
```

Contiene:

- `config.yaml`;
- `.env` con credenciales y variables de entorno;
- logs del gateway;
- sandboxes;
- cache;
- estado del runtime.

Reglas:

```text
No versionar secretos de /home/neoalmasana/.hermes/.env.
No leer ni copiar valores de tokens/API keys en reportes.
Solo se pueden listar nombres de variables cuando sea necesario.
```

---

### 1.4 Workspace Docker de Hermes

```text
/workspace
```

Uso:

- ruta interna dentro del container/sandbox Docker de Hermes.

Mapeo esperado cuando `docker_mount_cwd_to_workspace: true`:

```text
/workspace -> /opt/smartpyme-factory/repos/SmartPyme
```

Regla:

```text
/workspace es válido solo dentro del runtime Docker de Hermes y solo si contiene el repo SmartPyme montado.
```

Validación mínima dentro del container:

```bash
pwd
test -f GPT.md
test -f AGENTS.md
test -d .git
git branch --show-current
```

Si Git falla con `dubious ownership`, configurar solo el sandbox:

```bash
git config --global --add safe.directory /workspace
```

---

## 2. Rutas válidas por contexto

| Contexto | Ruta válida | Uso |
|---|---|---|
| VM host | `/opt/smartpyme-factory/repos/SmartPyme` | código SmartPyme |
| VM host | `/opt/smartpyme-factory/repos/hermes-agent` | Hermes externo |
| VM host | `/home/neoalmasana/.hermes/` | config/runtime Hermes |
| Docker Hermes | `/workspace` | repo SmartPyme montado |
| GitHub | `smartdash-almasana/SmartPyme` | fuente remota versionada |

---

## 3. Rutas deprecated o no canónicas

### 3.1 Ruta histórica incorrecta

```text
/home/neoalmasana/smartpyme-factory/repos/SmartPyme
```

Estado:

```text
DEPRECATED / NO CANONICA
```

Motivo:

- causó `BLOCKED_WRONG_CWD`;
- no coincide con el repo real validado en la VM persistente;
- puede existir en Cloud Shell u otros entornos, pero no es la ruta operativa de la VM `smartpyme-factory`.

---

### 3.2 Rutas Cloud Shell

Ejemplos:

```text
/home/neoalmasana/smartpyme-factory/repos/SmartPyme
~/smartpyme-factory/repos/SmartPyme
cs-* hostnames
```

Estado:

```text
NO PERSISTENTES / NO RUNTIME
```

Regla:

```text
Cloud Shell puede servir para inspección temporal, pero no es runtime operativo persistente de Hermes.
```

---

### 3.3 Clones temporales de agentes

Ejemplo detectado:

```text
/home/neoalmasana/.gemini/tmp/smartpyme/SmartPyme_fresh
```

Estado:

```text
TEMPORAL / NO CANONICO
```

Regla:

```text
No ejecutar factory loop, Ruff, commits ni cambios persistentes desde clones temporales de agentes.
```

---

## 4. Separación conceptual obligatoria

### 4.1 SmartPyme producto

Ruta:

```text
/opt/smartpyme-factory/repos/SmartPyme
```

Define:

- core de negocio;
- contratos;
- servicios;
- tests;
- factory loop versionado;
- documentación del producto.

---

### 4.2 Hermes Agent externo

Ruta:

```text
/opt/smartpyme-factory/repos/hermes-agent
```

Define:

- software orquestador;
- gateway;
- CLI;
- ejecución multiagente.

No es el core de SmartPyme.

---

### 4.3 Hermes Runtime

Ruta:

```text
/home/neoalmasana/.hermes/
```

Define:

- configuración real de Hermes;
- credenciales locales;
- logs;
- sandboxing;
- cache;
- estado del gateway.

No pertenece al repo SmartPyme y no se sincroniza por `git pull`.

---

### 4.4 Documentación Hermes dentro de SmartPyme

Ejemplos:

```text
HERMES.md
docs/factory/HERMES_DOCUMENTATION_INDEX.md
docs/factory/ROUTES_CONTRACT.md
factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md
```

Uso:

- contratos operativos;
- reglas de integración;
- documentación versionada.

Regla:

```text
Estos archivos documentan cómo debe operar Hermes sobre SmartPyme; no son el runtime Hermes.
```

---

## 5. Reglas de validación obligatoria

Antes de cualquier operación de código en VM:

```bash
pwd
git remote -v
git branch --show-current
git status --short
```

Criterios esperados:

```text
PWD=/opt/smartpyme-factory/repos/SmartPyme
remote=https://github.com/smartdash-almasana/SmartPyme.git
branch=factory/ts-006-jobs-sovereign-persistence
```

Dentro de Docker Hermes, se acepta:

```text
PWD=/workspace
```

solo si:

```bash
test -f GPT.md
test -f AGENTS.md
test -d .git
```

---

## 6. Regla BLOCKED_WRONG_CWD

Responder `BLOCKED_WRONG_CWD` si:

- `pwd` no es `/opt/smartpyme-factory/repos/SmartPyme` en VM host;
- `pwd` no es `/workspace` en Docker Hermes con repo montado;
- el remote Git no apunta a `smartdash-almasana/SmartPyme`;
- la rama no es la rama operativa esperada para la tarea;
- se detecta Cloud Shell como runtime persistente.

Formato de bloqueo:

```text
VEREDICTO: BLOCKED_WRONG_CWD
PWD_ACTUAL: <pwd>
PWD_ESPERADO: /opt/smartpyme-factory/repos/SmartPyme o /workspace montado
REMOTE_ACTUAL: <remote>
BRANCH_ACTUAL: <branch>
ACCION_REQUERIDA: moverse a ruta canónica antes de operar
```

---

## 7. Reglas de sincronización GitHub ↔ VM

GitHub:

```text
smartdash-almasana/SmartPyme
```

VM:

```text
/opt/smartpyme-factory/repos/SmartPyme
```

Flujo correcto cuando GPT escribe en GitHub:

1. GPT escribe en la rama autorizada de GitHub.
2. Hermes ejecuta `git pull --ff-only` desde `/opt/smartpyme-factory/repos/SmartPyme`.
3. Hermes verifica `git log -3 --oneline`.
4. Hermes ejecuta test o check focalizado.

No usar Cloud Shell como paso intermedio persistente.

---

## 8. Reglas para Hermes config

Archivo real:

```text
/home/neoalmasana/.hermes/config.yaml
```

Valores esperados para operar SmartPyme:

```yaml
terminal:
  cwd: /opt/smartpyme-factory/repos/SmartPyme
  docker_mount_cwd_to_workspace: true
```

Modelo esperado de convivencia:

```yaml
model:
  default: gpt-5.3-codex
  provider: openai-codex
```

Gemini debe invocarse explícitamente como auditor cuando corresponda:

```bash
hermes chat --provider gemini -m gemini-2.5-pro -q "..."
```

---

## 9. Tabla de decisión rápida

| Necesidad | Ruta |
|---|---|
| Tocar código SmartPyme | `/opt/smartpyme-factory/repos/SmartPyme` |
| Pull desde GitHub | `/opt/smartpyme-factory/repos/SmartPyme` |
| Configurar Telegram/Hermes | `/home/neoalmasana/.hermes/` |
| Revisar Hermes Agent externo | `/opt/smartpyme-factory/repos/hermes-agent` |
| Operar desde Docker Hermes | `/workspace` |
| Documentar integración Hermes-SmartPyme | repo SmartPyme, `docs/factory/**` |

---

## 10. Conclusión operativa

La verdad canónica queda fijada así:

```text
SMARTPYME_REPO_VM=/opt/smartpyme-factory/repos/SmartPyme
HERMES_AGENT_REPO_VM=/opt/smartpyme-factory/repos/hermes-agent
HERMES_RUNTIME=/home/neoalmasana/.hermes
HERMES_DOCKER_WORKSPACE=/workspace
GITHUB_REPO=smartdash-almasana/SmartPyme
```

Toda ruta distinta debe considerarse histórica, temporal o inválida hasta verificación explícita.
