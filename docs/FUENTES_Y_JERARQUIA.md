# FUENTES Y JERARQUÍA — GOBERNANZA DOCUMENTAL SMARTPYME

## 1) Objetivo

Definir una jerarquía única de fuentes para eliminar ambigüedad de naming, flujo y contratos operativos.

## 2) Jerarquía normativa (de mayor a menor)

### Nivel A — Canónico vinculante
1. `docs/ARQUITECTURA_NORMALIZADA.md`
2. SMARTCOUNTER MASTER BLUEPRINT v2 (siempre que exista copia controlada interna)
3. SMARTCOUNTER CONSISTENCY & VALIDATION FRAMEWORK (siempre que exista copia controlada interna)
4. SMARTCOUNTER CORE SYSTEM ARCHITECTURE (siempre que exista copia controlada interna)
5. Onboarding correcto y único de SmartPyme (solo para dominio comercial; no para pipeline técnico)

### Nivel B — Código vivo (fuente de implementación)
1. `app/core/clarification/service.py` (equivalente técnico de `clarification_service.py`)
2. `app/core/orchestrator/pipeline.py` (equivalente operativo de `run_pipeline.py` no encontrado)
3. `app/core/orchestrator/service.py`
4. `app/core/validation/service.py`
5. `factory/run_factory.py`
6. `factory/continuous_factory.py`

### Nivel C — Referencia auxiliar (no canónica)
1. `docs/smarttimes_full_architecture.md`
2. `docs/80.000pdf.md`
3. `docs/topologia.txt`
4. `prompt_engine.html` (no encontrado)
5. `premium_pitch_deck` (no encontrado)
6. `landing html` (no encontrado)
7. `writer sandbox` (no encontrado)
8. `Exceland docs` fuera del set activo SmartPyme Core (no encontrado)

## 3) Reglas de desempate

- Si Nivel A y B divergen en naming/flujo, prevalece Nivel A y se agenda ajuste de código o documentación según impacto.
- Si Nivel C contradice A o B, Nivel C se marca deprecable y se archiva en `docs/archive/FUENTES_DEPRECABLES.md`.
- Ningún documento comercial puede redefinir estados técnicos del pipeline.

## 4) Plan de depuración documental (ejecución)

### Fase 1 — Congelamiento semántico (inmediata)
- Congelar naming oficial: SmartPyme / SmartCounter Core / hallazgos.
- Congelar ley: IA interpreta; kernel decide.
- Congelar pipeline técnico canónico y estados canónicos.

### Fase 2 — Inventario y etiquetado (corto plazo)
- Catalogar cada documento como: `canonico`, `codigo_vivo`, `auxiliar`, `deprecable`.
- Detectar duplicados por tema: blueprint, consistency/validation, core architecture, base operativo.

### Fase 3 — Archivo controlado (corto plazo)
- Mover referencias contradictorias a `docs/archive/` o marcarlas como despriorizadas.
- Mantener trazabilidad de por qué se degradan y qué fuente las reemplaza.

### Fase 4 — Gate de continuidad (obligatorio)
- No continuar trabajo de canteras sin verificación documental:
  - naming oficial sin SmartSync como principal,
  - pipeline técnico canónico completo,
  - separación onboarding comercial vs core técnico,
  - regla de bloqueo `AWAITING_VALIDATION`.

## 5) Política de cambios de esta gobernanza

- Todo cambio a Nivel A requiere actualización simultánea de este índice y registro de deprecables.
- Se prohíben cambios implícitos por archivos auxiliares o material de pitch.

