# AI Provider Routing Contract — SmartPyme Factory

**Estado:** CANONICO v2
**Reemplaza:** CANONICO v1 (obsolescencia por migración de runtime a DeepSeek v4 Pro)

---

## Runtime Vigente

El runtime real de Hermes está definido en:

```text
/home/neoalmasana/.hermes/config.yaml
```

No asumir proveedores ni modelos sin leer ese archivo.

---

## Routing Activo (2026-05-04)

| Rol | Provider | Modelo | Estado |
| :--- | :--- | :--- | :--- |
| **Default / Orquestador** | `openrouter` | `deepseek/deepseek-v4-pro` | ACTIVO |
| **Fallback automático** | `openrouter` | `google/gemini-2.5-pro` | ACTIVO |
| **Gemini vía Google directo** | `vertex` o `google` | (no activo como provider Hermes) | OBJETIVO |
| **Codex** | `openai-codex` | `gpt-5.3-codex` (externo) | BAJO DEMANDA |
| **Gemma / Ollama / Qwen** | — | — | FUERA DE BASELINE |

---

## Regla Rectora

- **DeepSeek v4 Pro** es el modelo operativo primario (lectura, auditoría, construcción, orquestación).
- **Gemini 2.5 Pro** es fallback automático si DeepSeek no responde (rate limit, timeout, 529).
- **Gemini vía Google directo** (Vertex AI o Google AI Studio) es el **camino objetivo** para independizar el fallback de OpenRouter.
- **Codex** se invoca explícitamente desde fuera de Hermes para refactors delicados o migraciones con suite de tests.
- **Owner** decide.

---

## Tabla de Enrutamiento (Runtime Real)

| Escenario | Provider | Modelo |
| :--- | :--- | :--- |
| Ciclo normal Hermes (default) | `openrouter` | `deepseek/deepseek-v4-pro` |
| Fallback automático | `openrouter` | `google/gemini-2.5-pro` |
| Gemini directo (objetivo, no activo) | `vertex` / `google` | (a definir al activar) |
| Codex (bajo demanda externa) | `openai-codex` | (invocado fuera de Hermes) |

---

## Punto Único de Falla Actual

OpenRouter es el **único provider** para el modelo principal y su fallback. Si OpenRouter sufre degradación, rate limit extremo o outage, Hermes queda sin capacidad de razonamiento.

### Camino objetivo de remediación

1. Activar **Gemini vía Vertex AI** con ADC (`gcloud auth application-default print-access-token`) como provider nativo en Hermes.
2. Alternativa: **Gemini vía Google AI Studio / Gemini API** (`GEMINI_API_KEY` o `GOOGLE_API_KEY`).
3. Una vez activo, mover el fallback de `openrouter/google/gemini-2.5-pro` a Gemini directo, logrando diversidad real de providers.

---

## Reglas Operativas

1. **Default**: `deepseek/deepseek-v4-pro` vía OpenRouter. No modificar sin TaskSpec.
2. **Fallback**: `google/gemini-2.5-pro` vía OpenRouter. Automático ante 429, 529, 503 o timeout.
3. **Gemini directo**: objetivo profesional para eliminar el punto único de falla. No está activo como provider Hermes hoy.
4. **Codex**: solo bajo demanda explícita del Owner para refactors delicados o migraciones. No es provider activo de Hermes.
5. **Gemma / Ollama / Qwen**: removidos del baseline. No usar, no referenciar como activos.
6. **Soberanía**: el Owner decide sobre activación de nuevos providers y sobre productos finales.

---

## Verificación de Runtime

```bash
grep -A2 "^model:" /home/neoalmasana/.hermes/config.yaml
grep -A4 "^fallback_model:" /home/neoalmasana/.hermes/config.yaml
```

---

## Historial de Cambios

- **2026-05-04** — CANONICO v2: refleja runtime real (DeepSeek v4 Pro + Gemini 2.5 Pro vía OpenRouter). Documenta OpenRouter como punto único de falla. Marca Gemini directo como objetivo. Retira gemma4:e2b, gemini-3.1-flash-lite-preview, custom:vertex-gemini y ollama-local del contrato.
- **2026-04-28** — CANONICO v1 (original, obsoleto).
