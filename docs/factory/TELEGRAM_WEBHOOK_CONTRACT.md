# Telegram Contract v2.1 — SmartPyme Factory

## Modo vigente

- Desarrollo y VM inicial: long polling via Hermes Gateway.
- Webhook queda diferido hasta existir `secret_token` y endpoint estable.

## Identidad

La autorización se basa en `from_user.id`.

`chat_id` no es identidad suficiente.

Fuente esperada:

```text
factory/ai_governance/telegram_allowlist.yaml
```

## Callback seguro

Telegram limita `callback_data` a 64 bytes.

SmartPyme usa token table local:

1. Generar `callback_id = secrets.token_urlsafe(16)`.
2. Guardar en SQLite: `callback_id`, `cycle_id`, `action`, `expires_at`.
3. Enviar solo `callback_id` como `callback_data`.
4. Validar vigencia al recibir.

## MarkdownV2

Todo mensaje con `parse_mode=MarkdownV2` debe pasar por `factory.control.telegram_escape.escape_markdown_v2`.

## Rate limit

- 1 mensaje por segundo por chat.
- Ante 429: backoff 1s, 2s, 4s, 8s y respetar `Retry-After` si existe.

## Segmentación

Mensajes mayores a 4096 caracteres deben dividirse y numerarse.

## Estados de error

```json
{"status":"error","code":"UNAUTHORIZED|RATE_LIMITED|INVALID_COMMAND","message":"..."}
```
