# Tarea: Rediseño de TS_026C (Catálogo Clínico-Operativo)

## 1. Objetivo
Actualizar el diseño del catálogo `SymptomPathologyCatalog` para integrar plenamente la capa de conocimiento, investigación y elaboración del caso, tal como define `docs/architecture/KNOWLEDGE_RESEARCH_AND_CASE_LAYER.md`.

## 2. Definición del Rediseño Técnico
Cada entrada del catálogo `symptom_pathology_catalog` debe ser estructurada para ser utilizada por el motor de investigación operativa. La estructura final para cada síntoma será:

```yaml
symptom_id: str
required_knowledge: list[str]      # Conocimiento teórico faltante (dominio/método)
source_candidates: list[str]       # Fuentes o Tanques de conocimiento recomendados
research_questions: list[str]      # Preguntas disparadoras para la investigación
evidence_required: list[str]       # Evidencia técnica/documental necesaria
mayeutic_questions: list[str]      # Preguntas precisas al dueño (toma de evidencia)
candidate_skills: list[str]        # Skills técnicas de investigación
candidate_pathologies: list[str]   # Patologías posibles a investigar
```

## 3. Implicancias para TS_026C
- El catálogo ya no es una simple base de mapeo, sino un **disparador de ejecución** para la capa de investigación.
- La ejecución del flujo `Dolor → Síntoma → Hipótesis → Investigación → Diagnóstico` dependerá de la completitud de estos campos para cada `symptom_id`.
- Los `required_knowledge` deben estar alineados con los tanques de conocimiento definidos en la arquitectura (Transversales, Sectoriales, Específicos).
- Las `research_questions` guiarán al agente en la fase de consulta a fuentes externas bajo demanda (MCP/plugins).

## 4. Próximos pasos
- Migrar las definiciones actuales del catálogo para adoptar esta nueva estructura.
- Asegurar que la implementación en `app/catalogs/symptom_pathology_catalog.py` soporte estos nuevos campos sin romper la retrocompatibilidad con las interfaces existentes.
