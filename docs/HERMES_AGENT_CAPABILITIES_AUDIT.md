# Auditoría de Capacidades de Hermes-Agent

Este documento resume las capacidades reales del `AIAgent` de `hermes-agent` para su uso como runtime programático dentro de SmartPyme.

## Veredicto de Auditoría

`AIAgent` es un runtime viable y seguro para la operación conversacional de SmartPyme. Su configuración permite un aislamiento estricto y un mapeo directo entre los `jobs` de SmartPyme y las sesiones de conversación de Hermes, siempre que se aplique una configuración de seguridad rigurosa a través de un wrapper.

## Capacidades Reales de AIAgent

| Capacidad | Evidencia (Archivo y Función/Clase) | Conclusión |
| :--- | :--- | :--- |
| **Runtime Programático** | `run_agent.py` (`AIAgent`) | La clase `AIAgent` es la interfaz principal para la ejecución programática. |
| **Control de Tools (Allow-list)** | `run_agent.py` (`AIAgent.__init__`) | El parámetro `enabled_toolsets` permite crear una lista blanca estricta de toolsets. |
| **Control de Tools (Deny-list)** | `run_agent.py` (`AIAgent.__init__`) | El parámetro `disabled_toolsets` permite bloquear toolsets específicos. |
| **Descubrimiento MCP** | `tools/mcp_tool.py` (`discover_mcp_tools`) | El agente descubre y registra automáticamente las tools de servidores MCP configurados en `~/.hermes/config.yaml`. |
| **ID de Conversación** | `run_agent.py` (`AIAgent.__init__`) | Se puede fijar un `session_id` explícito, permitiendo el mapeo directo con sistemas externos como el `job_id` de SmartPyme. |
| **Inyección de Prompt** | `run_agent.py` (`AIAgent.__init__`) | `ephemeral_system_prompt` permite inyectar reglas de comportamiento en cada turno sin contaminar el historial. |
| **Control de Contexto** | `run_agent.py` (`AIAgent.__init__`) | `skip_context_files=True` previene la carga de `AGENTS.md` y otros archivos de contexto del filesystem. |
| **Control de Memoria** | `run_agent.py` (`AIAgent.__init__`) | `skip_memory=True` previene el uso de la memoria persistente de Hermes (`MEMORY.md`, `USER.md`). |

## Puntos Críticos de Integración

### Toolset MCP para SmartPyme

La auditoría confirma que `mcp_tool.py` registra un toolset por cada servidor MCP usando el nombre del servidor como identificador.
- **Evidencia**: `tools/mcp_tool.py`, función `_register_server_tools` llama a `_register_one_tool` con `toolset=server_name`.
- **Conclusión**: Para un servidor MCP definido como `smartpyme` en la configuración de Hermes, el nombre del toolset a utilizar es `smartpyme`.

### `session_id` vs. `task_id`

- **`session_id`**: Es el identificador de la **conversación completa**. Se puede fijar en el constructor de `AIAgent` y se usa para nombrar el archivo de trayectoria (`session_<session_id>.json`) y para agrupar mensajes en la base de datos `state.db`. **Este es el ID que debe mapearse al `job_id` de SmartPyme.**
- **`task_id`**: Es un identificador para **sesiones de herramientas específicas** y de corta duración (ej. una sesión de terminal). No representa la conversación principal y no debe usarse para el mapeo de jobs.

### Almacenamiento de Conversación (Trajectory)

La trayectoria completa de una conversación, incluyendo todas las tool calls y respuestas, es guardada por Hermes en dos lugares:
1.  **Archivo de Trayectoria**: Un archivo JSON detallado en `~/.hermes/sessions/session_<session_id>.json`.
2.  **Base de Datos de Estado**: Registros en la base de datos SQLite `~/.hermes/state.db`, indexados por `session_id`.

## Parcial o No Evidenciado

- **Wildcard en `disabled_toolsets`**: Aunque el wildcard `*` se usa internamente en `toolsets.py` para *expandir* a todos los nombres de tools, no hay evidencia de que `disabled_toolsets=['*']` funcione como un mecanismo de "denegar todo excepto lo habilitado". La estrategia de seguridad debe basarse en la lista blanca de `enabled_toolsets`, no en una lista de denegación.
- **Nombres Canónicos de Todos los Toolsets**: La auditoría se centró en los toolsets peligrosos más obvios (`terminal`, `file`, etc.). Una lista exhaustiva de todos los toolsets posibles requeriría auditar todas las extensiones de `hermes-agent`. La estrategia de `enabled_toolsets` mitiga este riesgo.
