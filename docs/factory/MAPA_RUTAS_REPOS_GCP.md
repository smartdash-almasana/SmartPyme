# Mapa de rutas, repositorios e instancia GCP — SmartPyme Factory

Estado: CANONICO v1

Este archivo existe para evitar operar en rutas equivocadas. Toda indicacion operativa debe partir de una ruta absoluta.

## Instancia GCP activa

| Campo | Valor |
|---|---|
| Proyecto GCP | `smartseller-490511` |
| VM | `smartpyme-factory` |
| Zona | `us-central1-a` |
| Usuario Linux | `neoalmasana` |
| Home usuario | `/home/neoalmasana` |

### Entrar a la VM desde Cloud Shell

```bash
gcloud compute ssh smartpyme-factory --zone us-central1-a --project smartseller-490511
```

### Listar instancias si hay duda

```bash
gcloud compute instances list --project smartseller-490511
```

## Regla obligatoria de trabajo

Todo comando debe incluir ruta absoluta antes de operar.

Formato correcto:

```bash
cd /ruta/absoluta && comando
```

Formato incorrecto:

```bash
comando
```

## Repositorios reales en la VM

### 1. SmartPyme — repo principal

| Campo | Valor |
|---|---|
| Ruta absoluta | `/opt/smartpyme-factory/repos/SmartPyme` |
| GitHub | `https://github.com/smartdash-almasana/SmartPyme.git` |
| Rama principal | `main` |
| Uso | Fuente de verdad de SmartPyme Factory: documentos canonicos, TaskSpecs, evidencia, control, core y gobernanza. |
| Operacion normal | SI |

Comando base:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && git status --short
```

Actualizar desde GitHub:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && git pull --ff-only origin main
```

Contenido relevante:

| Ruta | Para que sirve |
|---|---|
| `ChatGPT.md` | Entrada obligatoria para ChatGPT Director-Auditor. |
| `GPT.md` | Entrada previa/alias operativo de GPT. |
| `AGENTS.md` | Reglas generales de agentes. |
| `CODEX.md` | Reglas de uso para Codex. |
| `GEMINI.md` | Reglas de uso para Gemini. |
| `docs/factory/` | Contratos, manuales y gobernanza de factoria. |
| `factory/ai_governance/tasks/` | Cola versionada de TaskSpecs. |
| `factory/ai_governance/skills/` | Definicion versionada de skills de gobernanza. |
| `factory/evidence/` | Evidencia de ejecuciones, auditorias y ciclos. |
| `factory/control/` | Gate, estado, siguiente ciclo y control operativo. |
| `prompts/` | Prompts versionados para agentes. |

### 2. Hermes Agent — repo del orquestador

| Campo | Valor |
|---|---|
| Ruta absoluta | `/opt/smartpyme-factory/repos/hermes-agent` |
| GitHub | `https://github.com/smartdash-almasana/hermes-agent.git` |
| Rama principal | `main` |
| Uso | Codigo fuente editable de Hermes Agent instalado en la VM. |
| Operacion normal | Solo para configurar o diagnosticar Hermes. |

Comando base:

```bash
cd /opt/smartpyme-factory/repos/hermes-agent && git status --short
```

Buscar logica de gateway:

```bash
cd /opt/smartpyme-factory/repos/hermes-agent && grep -R "TELEGRAM_BOT_TOKEN\|Platform.TELEGRAM\|quick_commands" -n gateway cli.py hermes_cli --exclude-dir=__pycache__ | head -120
```

### 3. Backup historico SmartPyme — no operar

| Campo | Valor |
|---|---|
| Ruta absoluta | `/opt/smartpyme-factory/repos/SmartPyme_dirty_backup_20260427_012904` |
| GitHub | `https://github.com/smartdash-almasana/SmartPyme.git` |
| Uso | Backup historico local. No es runtime activo. |
| Operacion normal | NO |

Regla:

```text
No editar. No ejecutar. No usar como fuente de verdad. Solo borrar o archivar bajo decision explicita.
```

## Hermes instalado en home

| Elemento | Ruta |
|---|---|
| Hermes home | `/home/neoalmasana/.hermes` |
| Hermes CLI | `/home/neoalmasana/.hermes/venv/bin/hermes` |
| Config local | `/home/neoalmasana/.hermes/config.yaml` |
| Variables secretas | `/home/neoalmasana/.hermes/.env` |
| Lock gateway | `/home/neoalmasana/.hermes/gateway.lock` |
| Logs Hermes | `/home/neoalmasana/.hermes/logs` |
| Sesiones Hermes | `/home/neoalmasana/.hermes/sessions` |
| Skills instaladas | `/home/neoalmasana/.hermes/skills` |

Comandos base Hermes:

```bash
cd /home/neoalmasana && /home/neoalmasana/.hermes/venv/bin/hermes gateway status
```

```bash
cd /home/neoalmasana && /home/neoalmasana/.hermes/venv/bin/hermes gateway run --replace
```

```bash
cd /home/neoalmasana && /home/neoalmasana/.hermes/venv/bin/hermes gateway setup
```

## Archivos locales que nunca se suben a GitHub

| Archivo | Contiene | Regla |
|---|---|---|
| `/home/neoalmasana/.hermes/.env` | tokens, API keys, allowlists | NO commitear |
| `/home/neoalmasana/.hermes/config.yaml` | configuracion local de Hermes | NO commitear si contiene secretos |
| `/home/neoalmasana/.hermes/gateway.lock` | lock local del gateway | NO commitear |

## Procesos legacy que no deben operar la factoria

```text
telegram_factory_control.py
hermes_factory_runner.py
```

Verificar:

```bash
cd /home/neoalmasana && ps -ef | grep -E "telegram_factory_control|hermes_factory_runner" | grep -v grep || true
```

## Flujo correcto de trabajo diario

### 1. Entrar a la VM

```bash
gcloud compute ssh smartpyme-factory --zone us-central1-a --project smartseller-490511
```

### 2. Actualizar repo principal

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && git pull --ff-only origin main
```

### 3. Revisar estado del repo

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && git status --short
```

### 4. Revisar Hermes

```bash
cd /home/neoalmasana && /home/neoalmasana/.hermes/venv/bin/hermes gateway status
```

### 5. Revisar procesos legacy

```bash
cd /home/neoalmasana && ps -ef | grep -E "telegram_factory_control|hermes_factory_runner" | grep -v grep || true
```

## Fuente de verdad

Orden de autoridad:

```text
1. GitHub main de smartdash-almasana/SmartPyme
2. /opt/smartpyme-factory/repos/SmartPyme actualizado
3. Evidencia en factory/evidence/
4. Gate y estado en factory/control/
5. TaskSpecs en factory/ai_governance/tasks/
6. Hermes local en /home/neoalmasana/.hermes
7. Memoria conversacional
```

Si hay contradiccion, gana el repo principal y la evidencia.

## Nota operativa para ChatGPT

Cada respuesta con comandos debe incluir path completo.

Ejemplo correcto:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && git status --short
```

Ejemplo incorrecto:

```bash
git status --short
```
