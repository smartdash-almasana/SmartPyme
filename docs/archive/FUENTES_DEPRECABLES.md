# FUENTES DEPRECABLES / DEGRADADAS

## 1) Propósito

Registrar fuentes que no deben gobernar arquitectura activa de SmartPyme, con motivo y acción.

## 2) Registro activo

| fuente | estado | accion | reemplazo_canonico | motivo |
|---|---|---|---|---|
| Duplicados del SMARTCOUNTER MASTER BLUEPRINT v2 | deprecable | archivar o despriorizar | `docs/ARQUITECTURA_NORMALIZADA.md` + Blueprint controlado | Evitar versiones paralelas de arquitectura base. |
| Duplicados del SMARTCOUNTER CONSISTENCY & VALIDATION FRAMEWORK | deprecable | archivar o despriorizar | `docs/ARQUITECTURA_NORMALIZADA.md` + Framework controlado | Evitar reglas contradictorias de validación/bloqueo. |
| Duplicados del Documento Base del Sistema Operativo | deprecable | archivar o despriorizar | `docs/ARQUITECTURA_NORMALIZADA.md` | Consolidación en constitución documental única. |
| `docs/archive/smarttimes_full_architecture.md` | auxiliar_degradada | archivado como referencia histórica | `docs/SMARTPYME_OS_ACTUAL.md` | Contiene menciones no canónicas (ej. n8n) y naming mixto. |
| `docs/archive/80.000pdf.md` | auxiliar_degradada | archivado y no usar como contrato arquitectónico | `docs/SMARTPYME_OS_ACTUAL.md` | Documento de propuesta general no alineado al core canónico actual. |
| `docs/topologia.txt` | auxiliar_degradada | conservar como contexto histórico, no como norma | `docs/FUENTES_Y_JERARQUIA.md` | Texto base útil pero no contractual ni estable. |
| `prompt_engine.html` | no_encontrado | registrar y bloquear uso como fuente primaria | `docs/FUENTES_Y_JERARQUIA.md` | Fuente auxiliar solicitada pero no trazable en repo. |
| `premium_pitch_deck` | no_encontrado | registrar y bloquear uso como fuente primaria | Onboarding comercial oficial | Material comercial no debe gobernar pipeline técnico. |
| `landing html` | no_encontrado | registrar y bloquear uso como fuente primaria | Onboarding comercial oficial | Activo de marketing, no contrato de arquitectura core. |
| `writer sandbox` | no_encontrado | registrar y bloquear uso como fuente primaria | `docs/FUENTES_Y_JERARQUIA.md` | Entorno experimental fuera de gobernanza core. |
| `Exceland docs` fuera del set activo SmartPyme Core | no_encontrado | registrar y bloquear uso como fuente primaria | `docs/FUENTES_Y_JERARQUIA.md` | Fuentes externas no controladas para decisiones de core. |
| Referencias con SmartSync como nombre principal | deprecable | reemplazar naming progresivamente | `docs/ARQUITECTURA_NORMALIZADA.md` | SmartSync queda como alias legado, no marca vigente. |
| Referencias de negocio con término findings como principal | deprecable | migrar a término hallazgos | `docs/ARQUITECTURA_NORMALIZADA.md` | Coherencia semántica negocio-core. |
| `run_pipeline.py` (referencia documental) | no_encontrado | mapear a equivalente técnico vigente | `app/core/orchestrator/pipeline.py` | Nombre solicitado no hallado con exactitud. |
| `smartcounter_adapter.py` (referencia documental) | no_encontrado | registrar ausencia y evitar dependencia documental | No encontrado | No existe archivo trazable con ese nombre exacto. |
| `clarification_service.py` (referencia documental) | no_encontrado | mapear a equivalente técnico vigente | `app/core/clarification/service.py` | Nombre solicitado no hallado con exactitud. |

## 3) Criterio de cierre de depuración

- No quedan documentos auxiliares usados como fuente primaria para decisiones del core.
- Toda referencia de arquitectura pasa por jerarquía A/B definida.
- Naming y pipeline quedan congelados en una sola constitución documental.

