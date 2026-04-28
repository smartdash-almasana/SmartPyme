# Hermes Professional Configuration — SmartPyme

## Estado objetivo

SmartPyme usa Hermes como canal profesional único de control:

```text
Telegram → Hermes Gateway → Skills → Subagentes → Repo
```

## Prohibido

- Runners caseros.
- Bots Telegram paralelos.
- Polling duplicado sobre el mismo bot token.
- Tokens dentro del repo.
- Configuración manual sin validación de estado.

## Archivos fuera del repo

Estos archivos viven en la VM y no se commitean:

```text
/home/neoalmasana/.hermes/.env
/home/neoalmasana/.hermes/config.yaml
/home/neoalmasana/.hermes/gateway.lock
```

## Variables requeridas

```env
TELEGRAM_BOT_TOKEN=<botfather_token>
TELEGRAM_ALLOWED_USERS=<telegram_numeric_user_id>
```

`GATEWAY_ALLOW_ALL_USERS=true` solo se permite para diagnóstico temporal.

## Configuración profesional

Usar el wizard oficial:

```bash
cd ~
~/.hermes/venv/bin/hermes gateway setup
```

Seleccionar Telegram, cargar token, cargar allowlist, elegir polling.

## Arranque profesional

Foreground para diagnóstico:

```bash
cd ~
~/.hermes/venv/bin/hermes gateway run --replace
```

Servicio estable cuando el usuario systemd esté operativo:

```bash
cd ~
~/.hermes/venv/bin/hermes gateway install
~/.hermes/venv/bin/hermes gateway start
~/.hermes/venv/bin/hermes gateway status
```

## Limpieza obligatoria de legacy

Antes de arrancar Hermes:

```bash
cd ~
~/.hermes/venv/bin/hermes gateway stop || true
pkill -9 -f "telegram_factory_control.py" || true
pkill -9 -f "hermes_factory_runner.py" || true
rm -f /home/neoalmasana/.hermes/gateway.lock
```

## Validación

```bash
cd ~
~/.hermes/venv/bin/hermes gateway status
ps -ef | grep -E "telegram_factory_control|hermes_factory_runner|hermes gateway|gateway run" | grep -v grep || true
```

Criterio de aceptación:

- `gateway status` muestra running.
- No hay `telegram_factory_control.py`.
- No hay `hermes_factory_runner.py`.
- Telegram no reporta `terminated by other getUpdates request`.
- Hermes recibe y responde mensajes reales.

## Relación con SmartPyme

Hermes no reemplaza el core. Hermes controla el canal y delega ejecución. El core de SmartPyme conserva las leyes de trazabilidad, validación humana y bloqueo ante incertidumbre.
