# ARQUITECTURA NORMALIZADA — SMARTPYME (CONSTITUCIÓN VIVA)

## 1) Alcance y autoridad

Este documento congela la semántica arquitectónica y de negocio de SmartPyme para evitar deriva documental.

Orden de autoridad para arquitectura técnica:
1. Este documento.
2. `docs/FUENTES_Y_JERARQUIA.md`.
3. Código vivo del core (`app/core/...`).
4. Material auxiliar histórico (solo referencia).

## 2) Nomenclatura oficial (freeze)

- Producto oficial: **SmartPyme**.
- Núcleo arquitectónico oficial: **SmartCounter Core**.
- **SmartSync**: alias legado, no usar como nombre principal en documentación nueva.
- Término de negocio oficial: **hallazgos**.
- Término `findings`: solo aceptable en contexto técnico legado o adapters transitorios.

## 3) Leyes del sistema (inmutables)

- Ley central: **IA interpreta; kernel decide**.
- Regla crítica de bloqueo: si `estado = AWAITING_VALIDATION`, el pipeline se bloquea.
- Onboarding comercial y pipeline técnico son dominios separados; no fusionar narrativas ni contratos.
- No usar `n8n` como componente canónico de arquitectura.

## 4) Pipeline técnico canónico (freeze)

Secuencia canónica:

`Ingesta -> Normalización -> Entity Resolution -> Clarification -> Orquestación -> Comparación -> Hallazgos -> Comunicación -> Acción`

## 5) Estados canónicos del flujo

`INGESTED -> NORMALIZED -> ENTITY_RESOLVED -> AWAITING_VALIDATION -> READY_FOR_COMPARISON -> COMPARISON_DONE -> FINDINGS_READY -> COMPLETED`

Política de ejecución:
- Si llega a `AWAITING_VALIDATION`, no avanzar a etapas posteriores.
- La salida de `Hallazgos` alimenta `Comunicación`; no saltear contratos por adapters temporales.

## 6) Acoples y transiciones vigentes

- `findingssignals` se considera adapter transitorio; no es contrato final del dominio.
- Cualquier documentación nueva debe expresar contratos en términos de `hallazgos`.
- Las decisiones de IA se materializan como propuestas; la confirmación final reside en el kernel y sus estados.

## 7) Separación obligatoria de dominios

### 7.1 Dominio técnico (core)
- Modelos, servicios y orquestación bajo `app/core`.
- Estados, bloqueo fail-closed y contratos determinísticos.

### 7.2 Dominio comercial (onboarding)
- Mensajería de adopción, pitch y material de venta.
- No define pipeline técnico, estados ni ley de decisión del kernel.

## 8) Fuentes canónicas declaradas para esta normalización

Base obligatoria (cuando exista copia controlada):
- SMARTCOUNTER MASTER BLUEPRINT v2
- SMARTCOUNTER CONSISTENCY & VALIDATION FRAMEWORK
- SMARTCOUNTER CORE SYSTEM ARCHITECTURE
- Onboarding correcto y único de SmartPyme
- `clarification_service.py` (no encontrado con ese nombre exacto; referencia técnica equivalente: `app/core/clarification/service.py`)
- `run_pipeline.py` (no encontrado con ese nombre exacto)
- `smartcounter_adapter.py` (no encontrado con ese nombre exacto)

## 9) Criterio operativo a partir de este documento

- Toda nueva pieza documental debe referenciar nombre oficial SmartPyme y pipeline canónico completo.
- Toda fuente con naming o flujo contradictorio pasa a estado deprecable/auxiliar.
- No continuar canteras sin respetar jerarquía documental definida en `docs/FUENTES_Y_JERARQUIA.md`.

