# Agent Context Budget — SmartPyme Factory

| Agente | Límite operativo inicial | Reserva prompt | Reserva tools | Reserva output | Política |
|---|---:|---:|---:|---:|---|
| Codex Builder | 200000 | 20000 | 40000 | 20000 | sliding window y evidencia resumida |
| Gemini Auditor | 1000000 | 50000 | 100000 | 50000 | relevance-based, descarta logs antiguos |
| GPT Director | 128000 | 20000 | 30000 | 20000 | compactar historial de decisión |

## Timeouts

- Codex build: 45 min.
- Gemini audit: 30 min.
- Director review: 60 min.
- Ciclo completo máximo: 180 min.
