# DeepSeek Audit Bridge

**Actualizado:** 2026-05-04 — corregido "DeepSeek local" → "DeepSeek v4 Pro vía OpenRouter (cloud)". Agregado punto único de falla y camino objetivo Gemini directo.

---

## Objetivo

DeepSeek v4 Pro es el modelo operativo primario de Hermes para **todas** las tareas (lectura, auditoría, construcción, orquestación). Se consume vía API cloud de OpenRouter, no localmente.

## Runtime real

- **Default Hermes:** `deepseek/deepseek-v4-pro` vía `openrouter`
- **Fallback automático:** `google/gemini-2.5-pro` vía `openrouter`
- **Contexto:** 128K tokens
- **Timeout:** 180s (default), 300s (fallback)

## Punto Único de Falla Actual

Ambos modelos — default y fallback — pasan por OpenRouter. Si OpenRouter sufre degradación, rate limit extremo o outage, Hermes queda sin capacidad de razonamiento.

### Camino objetivo de remediación

1. **Preferido:** Gemini vía **Vertex AI** con ADC (`gcloud auth application-default print-access-token`).
2. **Alternativo:** Gemini vía **Google AI Studio / Gemini API** (`GEMINI_API_KEY` o `GOOGLE_API_KEY`).
3. Una vez activo cualquiera de los dos, mover el fallback de `openrouter/google/gemini-2.5-pro` a Gemini directo, logrando diversidad real de providers.

**Estado actual:** Vertex AI y Google AI Studio **no están activos** como providers de Hermes. Son el objetivo profesional.

## Ruteo vigente

| Rol | Modelo | Provider |
| :--- | :--- | :--- |
| Auditor / Lector | `deepseek/deepseek-v4-pro` | `openrouter` |
| Builder / Refactor | `deepseek/deepseek-v4-pro` | `openrouter` |
| Orquestador | `deepseek/deepseek-v4-pro` | `openrouter` |
| Fallback | `google/gemini-2.5-pro` | `openrouter` |

## Agentes fuera del baseline

- **Gemma local:** removido. No usar.
- **Ollama / Qwen:** removidos. No usar.
- **Codex:** solo bajo demanda explícita externa, no integrado como provider Hermes.

## Salida de evidencia (convención)

Si se requiere evidencia de auditoría persistida en archivos:

```text
factory/evidence/deepseek_audit/<task_id>/audit_report.md
factory/evidence/deepseek_audit/<task_id>/verdict.txt
factory/evidence/deepseek_audit/<task_id>/files_reviewed.txt
```

`verdict.txt` acepta solo:
- `PASS`
- `PARTIAL`
- `BLOCKED`

## Reglas

- DeepSeek v4 Pro es el agente operativo primario. Ejecuta lectura, auditoría y construcción.
- Gemini 2.5 Pro es fallback automático (rate limit, timeout, error 529/503).
- La evidencia de auditoría debe quedar trazable en archivos o en el reporte de sesión.
- El Owner tiene la decisión final.

## Flujo

```text
TaskSpec → DeepSeek v4 Pro (OpenRouter) → evidencia → Owner decide
                    ↓ (si falla)
              Gemini 2.5 Pro (OpenRouter) → evidencia → Owner decide
```

## Historial

- **2026-05-04** — Corregido: "DeepSeek local" → cloud vía OpenRouter. Agregado punto único de falla y camino objetivo (Vertex AI preferido, Google AI Studio alternativo). Removidas referencias a Gemma local, Gemini Vertex como builder, y Ollama.
- **2026-04-28** — Versión original (obsoleta: asumía DeepSeek local y Gemma/Ollama activos).
