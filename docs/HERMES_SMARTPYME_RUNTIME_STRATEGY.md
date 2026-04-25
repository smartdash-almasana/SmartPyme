# Estrategia de Integración: Hermes + SmartPyme

Este documento define la arquitectura y configuración canónica para utilizar `hermes-agent` como el motor conversacional programático para SmartPyme.

## Arquitectura

La integración se basa en un wrapper (`HermesSmartPymeRuntime`) que encapsula y configura de forma segura la clase `AIAgent` de Hermes. Este wrapper actúa como el único punto de entrada para las interacciones del dueño, garantizando que el agente opere dentro de los límites definidos por SmartPyme.

```mermaid
graph TD
    A[Dueño] --> B{HermesSmartPymeRuntime};
    B -- Configura y encapsula --> C[hermes_agent.run_agent.AIAgent];
    C -- Solo usa toolset 'smartpyme' --> D[MCP (mcp_smartpyme_bridge.py)];
    D -- Ejecuta tools --> E[SmartPyme Core];
    E -- Persiste en --> F[(SmartPyme DB/State)];
    E -- Devuelve resultado --> D;
    D -- Devuelve resultado --> C;
    C -- Genera respuesta para el dueño --> B;
    B -- Comunica a --> A;

    style C fill:#cde4ff,stroke:#5a96e3,stroke-width:2px
    style E fill:#d5e8d4,stroke:#82b366,stroke-width:2px
```

## Flujo de Operación

1.  **Inicio**: El dueño inicia una interacción. El `HermesSmartPymeRuntime` crea un `job` en SmartPyme y obtiene un `job_id`.
2.  **Instanciación Segura**: El wrapper instancia `AIAgent` usando el `job_id` para construir un `session_id` único (e.g., `sp_job_<job_id>`) y aplicando la **Configuración Segura Canónica**.
3.  **Ejecución**: Se invoca el método `agent.run_conversation()` con el prompt del dueño.
4.  **Llamada a Tool**: `AIAgent`, limitado por `enabled_toolsets=['smartpyme']`, solo puede llamar a las tools expuestas por `mcp_smartpyme_bridge.py`.
5.  **Ejecución en Core**: El bridge recibe la llamada y la delega al core de SmartPyme, que es la única capa que modifica el estado (Jobs, Evidence, etc.).
6.  **Respuesta**: El resultado de la tool se devuelve a Hermes, que lo usa para formular una respuesta final al dueño.
7.  **Auditoría**: La conversación completa queda registrada en el archivo de trayectoria de Hermes (`session_sp_job_<job_id>.json`) y en la base de datos de estado (`state.db`), proveyendo una auditoría completa.

## Configuración Segura Canónica de AIAgent

El wrapper `HermesSmartPymeRuntime` **debe** instanciar `AIAgent` con la siguiente configuración:

```python
# dentro de HermesSmartPymeRuntime

from hermes_agent.run_agent import AIAgent

# ...

REGLAS_SISTEMA = (
    "Eres un agente operador de SmartPyme. Tu única función es usar exclusivamente las tools del toolset SmartPyme habilitado por el runtime "
    "para cumplir con la solicitud del usuario. No tienes acceso al filesystem, terminal ni a la web. "
    "Opera únicamente sobre el job actual. No respondas al usuario sin usar una tool. "
    "Si no puedes avanzar, declara el bloqueo."
)

agent = AIAgent(
    # Mapeo directo Job -> Conversación
    session_id=f"sp_job_{job_id}",

    # --- AISLAMIENTO DE TOOLS ---
    # Lista blanca estricta: solo se permite el toolset del MCP de SmartPyme.
    enabled_toolsets=["smartpyme"],
    # Lista de denegación como defensa en profundidad.
    disabled_toolsets=["terminal", "file", "code_execution", "delegation", "browser"],
    # NOTA: La seguridad primaria es la whitelist enabled_toolsets=['smartpyme'].
    # disabled_toolsets es defensa en profundidad y depende de los nombres reales de toolsets definidos por Hermes.

    # --- CONTROL DE CONTEXTO Y PROMPT ---
    # No cargar AGENTS.md ni otros archivos del filesystem.
    skip_context_files=True,
    # No usar la memoria persistente de Hermes (MEMORY.md/USER.md). La verdad está en SmartPyme.
    skip_memory=True,
    # Inyectar las reglas de operación en cada turno sin guardarlas en el historial.
    ephemeral_system_prompt=REGLAS_SISTEMA,
    
    # --- LÍMITES DE EJECUCIÓN ---
    # Prevenir loops infinitos o excesivos.
    max_iterations=15,
    
    # --- MODO PROGRAMÁTICO ---
    quiet_mode=True
)
```

## Implementación

El wrapper `HermesSmartPymeRuntime` ha sido implementado siguiendo esta estrategia y se encuentra en `app/runtime/hermes_smartpyme_runtime.py`. El test de validación de la configuración segura se encuentra en `tests/e2e/test_hermes_smartpyme_runtime.py`.
