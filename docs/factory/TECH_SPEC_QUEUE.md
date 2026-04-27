# TECH SPEC QUEUE — SmartPyme Factory

## Purpose
Repositorio vivo de ideas técnicas, especificaciones emergentes y líneas de evolución del sistema.

## Modo de uso
- Toda idea relevante se registra automáticamente aquí.
- Se clasifica luego como:
  - task
  - hallazgo
  - roadmap
- Se prioriza en ciclos posteriores.

---

## QUEUE

### [1] Core reconciliación v1
Origen: interacción usuario–GPT
Estado: promoted → task activa
Descripción:
Motor base para comparar dos fuentes tabulares y detectar diferencias por entidad.

---

### [2] Modelo canónico de hallazgos
Estado: pendiente
Descripción:
Definir estructura estándar:
- entidad
- campo
- valor fuente A
- valor fuente B
- diferencia cuantificada
- origen de datos

---

### [3] Normalización de inputs tabulares
Estado: pendiente
Descripción:
Resolver diferencias de schema:
- nombres de columnas
- tipos de datos
- formatos numéricos

---

### [4] Pipeline determinístico sin IA
Estado: pendiente
Descripción:
Asegurar que toda lógica core sea determinística y auditable.

---

## REGLAS DE GOBERNANZA

1. Nada se pierde: toda idea entra a esta cola.
2. Toda task debe provenir de esta cola o de hallazgos.
3. La cola se reordena por prioridad en cada ciclo.
4. El sistema debe poder auto-promover items a tasks.

---

## NEXT ACTION

- Integrar lectura automática de esta cola en Hermes
- Priorizar dinámicamente
- Sin intervención humana obligatoria
