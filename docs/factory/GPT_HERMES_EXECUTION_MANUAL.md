# GPT Hermes Execution Manual — Professional Mode

## Objetivo

Dejar Hermes Gateway como único sistema de control conversacional de SmartPyme:

```text
Telegram → Hermes Gateway → Skills → Subagentes → Repo
```

Este manual reemplaza cualquier flujo legacy basado en runners, bots paralelos o scripts caseros.

## Fuente normativa

Procedimiento basado en documentación oficial de Hermes:

- Telegram Gateway: `hermes gateway setup`, token de BotFather y allowlist numérica.
- Configuración: secretos en `~/.hermes/.env`, settings en `~/.hermes/config.yaml`.
- Delegation/Subagents: Hermes delega tareas con subagentes aislados.
- Skills: las capacidades se integran como skills de Hermes, no como loops paralelos.

## Reglas duras

- No crear runners.
- No crear bots paralelos.
- No ejecutar `scripts/telegram_factory_control.py`.
- No ejecutar `scripts/hermes_factory_runner.py`.
- No poner tokens en GitHub.
- No usar `GATEWAY_ALLOW_ALL_USERS=true` salvo diagnóstico temporal.
- Usar allowlist profesional: `TELEGRAM_ALLOWED_USERS=<telegram_numeric_user_id>`.
- Un solo proceso de polling por bot token.
- Si Telegram informa conflicto de polling, existe otro proceso usando el mismo token.

## Rutas reales esperadas en VM

```text
Hermes CLI:      /home/neoalmasana/.hermes/venv/bin/hermes
Hermes home:     /home/neoalmasana/.hermes
SmartPyme repo:  /opt/smartpyme-factory/repos/SmartPyme
Hermes repo:     /opt/smartpyme-factory/repos/hermes-agent
```

## Procedimiento estricto

### 1. Confirmar binario Hermes

```bash
cd ~
~/.hermes/venv/bin/hermes --version
```

Si falla, detener. No improvisar.

### 2. Limpiar procesos legacy

```bash
cd ~
~/.hermes/venv/bin/hermes gateway stop || true
pkill -9 -f "telegram_factory_control.py" || true
pkill -9 -f "hermes_factory_runner.py" || true
pkill -9 -f "hermes gateway" || true
rm -f /home/neoalmasana/.hermes/gateway.lock
ps -ef | grep -E "telegram_factory_control|hermes_factory_runner|hermes gateway|gateway run" | grep -v grep || true
```

Debe quedar sin procesos legacy.

### 3. Configurar secretos en `.env`

Archivo real:

```text
/home/neoalmasana/.hermes/.env
```

Contenido requerido:

```env
TELEGRAM_BOT_TOKEN=<botfather_token>
TELEGRAM_ALLOWED_USERS=<telegram_numeric_user_id>
```

No usar placeholders. No usar comillas. No agregar comandos `gcloud` dentro del archivo.

### 4. Configurar gateway con wizard oficial

```bash
cd ~
~/.hermes/venv/bin/hermes gateway setup
```

Obligatorio:

- Seleccionar Telegram.
- Ingresar token de BotFather.
- Ingresar Telegram user ID numérico.
- Elegir polling cuando el wizard lo solicite.

### 5. Arrancar gateway

```bash
cd ~
~/.hermes/venv/bin/hermes gateway run --replace
```

Mantener esa terminal abierta si se usa foreground.

### 6. Estado

En otra terminal SSH dentro de la VM:

```bash
cd ~
~/.hermes/venv/bin/hermes gateway status
```

Criterio:

- Gateway running.
- Sin conflicto de polling.
- Sin scripts legacy activos.

### 7. Prueba real

Enviar un mensaje al bot desde Telegram. Hermes debe recibirlo y responder desde el gateway.

## Si Telegram no aparece en setup

```bash
cd /opt/smartpyme-factory/repos/hermes-agent
grep -R "Platform.TELEGRAM\|Telegram Setup\|TELEGRAM_BOT_TOKEN" -n gateway cli.py hermes_cli website --exclude-dir=.venv --exclude-dir=__pycache__ | head -120
```

Conclusión válida únicamente con evidencia:

- build con adapter oculto;
- instalación incompleta;
- configuración inconsistente.

## Si hay conflicto de polling

```bash
cd ~
ps -ef | grep -E "telegram_factory_control|hermes_factory_runner|hermes gateway|gateway run|telegram" | grep -v grep
```

Si aparecen scripts legacy, detenerlos. Si no aparecen y el conflicto continúa, regenerar token en BotFather y reemplazarlo en `.env`.

## Success Criteria

- Hermes recibe mensajes reales de Telegram.
- Gateway activo.
- Sin `telegram_factory_control.py`.
- Sin `hermes_factory_runner.py`.
- Sin runners externos.
- Sin tokens en GitHub.

## Final Rule

Si no está confirmado en el sistema, no existe.
