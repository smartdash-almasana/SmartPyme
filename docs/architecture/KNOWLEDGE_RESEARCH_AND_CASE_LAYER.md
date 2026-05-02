# KNOWLEDGE_RESEARCH_AND_CASE_LAYER

## 1. Visión Operativa
La capa de conocimiento y caso integra el diagnóstico (basado en evidencia del cliente) con la investigación (basada en tanques de conocimiento). El core operativo mantiene la lógica, mientras que los tanques proveen contexto y la búsqueda externa aporta profundidad.

## 2. Estructura de Conocimiento
- **Tanques Transversales**: Reglas de negocio globales, doctrina Palantir, estándares contables.
- **Tanques Sectoriales**: Mejores prácticas por industria.
- **Tanques Específicos**: Casos de uso históricos de la propia SmartPyme.
- **Fuentes Externas**: Consultadas bajo demanda vía MCP/plugin para llenar brechas.

## 3. Flujo de Diagnóstico (Caso Operativo)
1. **Dolor** → **Síntoma** (Catálogo TS_026C).
2. **Patología Posible** (Hipótesis).
3. **Evidencia Requerida** (¿Qué tiene el cliente?).
4. **Conocimiento Requerido** (¿Qué nos falta saber?).
5. **Búsqueda Externa** (si `brecha_conocimiento > brecha_evidencia`).
6. **ReferenceBundle** (Investigación).
7. **OperationalCase** (Elaboración final).
8. **DiagnosticReport** (Entrega).

## 4. Diferenciación
- **Brecha de Evidencia**: Datos faltantes del cliente. Se solicita mediante preguntas mayéuticas.
- **Brecha de Conocimiento**: Falta de marco teórico para interpretar la evidencia. Se llena vía tanques o búsqueda externa.

## 5. Reglas de Gobernanza
- La fuente externa **orienta**, no define.
- La evidencia del cliente **prueba** la patología.
- Prohibida la entrada de datos externos sin **curación/versionado**.
- Core operativo **agnóstico** al dominio.
- Soberanía: SmartPyme propone; el dueño decide.

## 6. Integración TS_026C
El catálogo TS_026C es el disparador de este flujo, mapeando el síntoma a las skills, variables y evidencias necesarias para iniciar la investigación operativa.

## 7. Campos en OperationalCase
- `required_knowledge`: Conocimiento teórico faltante.
- `source_candidates`: Fuentes para investigar.
- `references_used`: Bundle de investigación final.
- `research_plan`: Pasos de la búsqueda.
- `knowledge_gaps`: Brechas no resueltas.
