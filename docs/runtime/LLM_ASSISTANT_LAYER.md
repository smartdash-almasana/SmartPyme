# LLM Assistant Layer (Telegram Conversacional)

## Objetivo
Agregar una capa LLM minima para mensajes conversacionales de Telegram sin reemplazar el runtime deterministico.

## Guardrails
- Solo mensajes conversacionales (texto libre).
- No se usa para pipeline XLSX/BEM.
- Grounding obligatorio con:
  - `summary`
  - `findings`
  - `operational_report`
- Si falla LLM, fallback deterministico actual (`unsupported_command`).
- No memoria persistente, no decisiones automaticas, no herramientas autonomas.

## Feature Flag
Habilitar:

```bash
ENABLE_LLM_ASSISTANT=true
```

Deshabilitar (default):

```bash
ENABLE_LLM_ASSISTANT=false
```

## Configuracion OpenCode/OpenRouter (free)
El servicio usa endpoint compatible OpenAI (`/chat/completions`) y permite configurar:

```bash
OPENROUTER_API_KEY=<token>
# alternativa compatible:
OPENCODE_API_KEY=<token>

# default si no se define:
# https://openrouter.ai/api/v1
OPENCODE_BASE_URL=https://openrouter.ai/api/v1

# prioridad sugerida para pruebas free:
OPENCODE_MODEL=gemma-4
# alternativas:
# qwen/qwen3-32b:free
# minimax/minimax-m1:free
# meta-llama/llama-3.3-70b-instruct:free
```

## Flujo
1. TelegramAdapter recibe update.
2. Si es comando (`/status`, `/auditar_venta_bajo_costo`, etc.) mantiene flujo actual.
3. Si es texto libre y `ENABLE_LLM_ASSISTANT=true`, invoca `OperationalAssistantService`.
4. El LLM responde corto, grounded.
5. Si hay error o respuesta vacia, fallback a comportamiento deterministico actual.

## Input del wrapper
`OperationalAssistantService.build_response(...)` recibe:
- `user_message`
- `summary`
- `findings`
- `operational_report`

## Output
- `str` corto para Telegram (modo `llm_assistant`) o `None` para fallback.
