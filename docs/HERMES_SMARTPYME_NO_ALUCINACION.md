# Protocolo Anti-Alucinación Hermes-SmartPyme

Este documento establece las reglas y mecanismos técnicos para asegurar que Hermes actúe como un operador determinístico de SmartPyme y no como una fuente de verdad independiente.

## Principio Fundamental

**Hermes es un operador conversacional, no una base de conocimiento.** La única fuente de verdad sobre el estado del negocio, los hallazgos y las evidencias es el **Core de SmartPyme**. Hermes no debe "recordar" hechos ni inferir estados; su función es traducir la intención del dueño en llamadas a las tools de SmartPyme y comunicar los resultados de vuelta.

## Reglas y Mecanismos de Enforcement

| # | Regla | Mecanismo de Enforcement | Capa Responsable | Tipo |
|:-:|:---|:---|:---|:---|
| 1 | **Aislamiento de Tools** | `enabled_toolsets=['smartpyme']` | **Wrapper** | `wrapper-required` |
|   | Hermes solo puede ver y ejecutar las tools del MCP de SmartPyme. | `disabled_toolsets` para defensa en profundidad. | **Wrapper** | `wrapper-required` |
| 2 | **Operación Basada en Evidencia** | El prompt fuerza a Hermes a usar `get_evidence` antes de responder. | Prompt Inyectado | `prompt-only` |
|   | Si una tool call (e.g., `get_evidence`) devuelve un error o un resultado vacío, Hermes debe informar del bloqueo. | Lógica de la tool en el bridge. | **Bridge** | `bridge-enforced` |
| 3 | **Prohibición de Memoria Externa** | `skip_memory=True` | **Wrapper** | `wrapper-required` |
|   | Se deshabilita el acceso a `MEMORY.md` y `USER.md` de Hermes. | La verdad reside en el `EvidenceStore` y `Facts` de SmartPyme. | **Core** | `core-enforced` |
| 4 | **Prohibición de Contexto Externo**| `skip_context_files=True` | **Wrapper** | `wrapper-required` |
|   | Se previene la carga automática de `AGENTS.md` y otros archivos del filesystem. | El contexto del job debe ser proveído explícitamente vía `ingest_document`. | **Wrapper/Core** | `wrapper-required` |
| 5 | **Prompt de Sistema Obligatorio** | `ephemeral_system_prompt` | **Wrapper** | `wrapper-required` |
|   | El wrapper inyecta en cada turno un set de instrucciones que define el rol de Hermes como operador restringido. | El prompt es efímero y no contamina el historial de la conversación. | Prompt Inyectado | `prompt-only` |
| 6 | **Límites de Ejecución** | `max_iterations=15` | **Wrapper** | `wrapper-required` |
|   | Se establece un límite superior de iteraciones (tool calls) por turno para prevenir loops. | | | |

## Prompt de Sistema Base (Inyectado)

El siguiente prompt (o una variante) **debe** ser inyectado usando `ephemeral_system_prompt`:

> "Eres un agente operador de SmartPyme. Tu única función es usar exclusivamente las tools del toolset SmartPyme habilitado por el runtime para cumplir con la solicitud del usuario. No tienes acceso al filesystem, terminal ni a la web. Opera únicamente sobre el job actual. No respondas al usuario sin usar una tool para obtener evidencia. Si una tool no devuelve la información que necesitas, informa que no puedes completar la solicitud por falta de evidencia. No inventes información."

## Relación con la Arquitectura de Datos de SmartPyme

- **RawDocument**: El material crudo (PDF, texto) que se ingiere con `ingest_document`.
- **EvidenceChunk**: Fragmentos procesados y vectorizados del `RawDocument`, recuperables vía `get_evidence`.
- **Fact**: Una pieza de información estructurada y validada, derivada de una `EvidenceChunk` y con trazabilidad completa. Hermes nunca crea `Facts` directamente.
- **Hallazgo (Finding)**: Una conclusión operativa generada por el **Core de SmartPyme** al comparar `Facts` o métricas. Hermes solo puede **comunicar** hallazgos, no generarlos.
