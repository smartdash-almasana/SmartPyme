# HALLAZGO

## META
- id: HZ-2026-04-27-FACTORY-006
- estado: pending
- modulo_objetivo: langchain-langgraph-evaluation
- prioridad: media
- origen: gpt-auditor
- repo_destino: SmartPyme

## OBJETIVO
Evaluar la introduccion de LangChain/LangGraph en SmartPyme sin contaminar el core deterministico.

## CONTEXTO
LangChain aporta interfaces estandarizadas para modelos, tools y structured output. LangGraph aporta ejecucion durable, checkpoints y workflows multi-step. SmartPyme ya usa Hermes como orquestador principal de factoria, por lo que LangChain/LangGraph debe evaluarse como capa opcional para workflows internos, no como reemplazo de Hermes ni del core.

## RUTAS_OBJETIVO
Se permite crear o modificar solo:

- docs/specs/09-langchain-langgraph-evaluation.md
- factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md

## RESTRICCIONES
- No agregar dependencias todavia
- No tocar codigo Python
- No tocar tests
- No reemplazar Hermes
- No reemplazar SmartPyme core
- No introducir agentes autonomos nuevos

## TAREAS_EJECUCION
1. Crear doc de evaluacion tecnica.
2. Definir usos permitidos:
   - structured output
   - workflows con checkpoint
   - human-in-the-loop
   - pipelines de ingesta/RAG futuros
3. Definir usos prohibidos:
   - logica de negocio en agentes
   - verdad del tenant en memoria LangChain
   - tool execution sin whitelist
4. Documentar riesgos de seguridad y dependencia.
5. Ajustar skill Hermes para mencionar que LangChain/LangGraph solo puede entrar con hallazgo explicito.

## CRITERIOS_DE_ACEPTACION
- Existe el documento de evaluacion.
- Menciona LangChain.
- Menciona LangGraph.
- Define usos permitidos y prohibidos.
- No se agrega dependencia.
- No se toca codigo Python.

## VALIDACIONES
```bash
git diff --name-only
grep -R "LangChain\|LangGraph" -n docs/specs/09-langchain-langgraph-evaluation.md factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md
```
