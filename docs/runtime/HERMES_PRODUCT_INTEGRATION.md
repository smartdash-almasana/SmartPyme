# Arquitectura: Hermes Runtime en Producto

Este documento describe la integración de una instancia de Hermes, específica para el producto, como la capa conversacional y de orquestación para el bot de Telegram.

## Separación de Runtimes: Producto vs. Factoría

Es crítico entender que existen **dos instancias de Hermes conceptualmente separadas**:

1.  **Hermes de Factoría:** Es el agente de alto privilegio utilizado para tareas de auditoría, refactor y operaciones sobre el código fuente. Su configuración le otor
ga acceso a herramientas de Filesystem, Git y otros componentes de la factoría.
2.  **Hermes de Producto:** Es una instancia de **bajo privilegio** cuyo único propósito es servir como capa de IA conversacional para el producto final (ej. el bot de Telegram). Su acceso a herramientas está estrictamente limitado.

**Esta integración se refiere exclusivamente al Hermes de Producto.**

## Soberanía del Kernel SmartPyme

El principio de diseño fundamental es que **el kernel determinístico de SmartPyme mantiene la autoridad final**.

-   **Hermes como Orquestador, no como Decisor:** Hermes no re-ejecuta diagnósticos ni altera la evidencia. Su función es **interpretar** los resultados (findings, summaries) que el kernel ya ha producido.
-   **Toolset de Solo Lectura:** El toolset permitido para Hermes Producto estará restringido a funciones que lean y procesen el contexto ya proporcionado (ej. "filtrar hallazgos de rentabilidad", "explicar un finding"). **No tendrá acceso a herramientas de escritura, filesystem o git.**
-   **Fallback Determinístico Obligatorio:** Si la capa de Hermes falla por cualquier motivo (error de modelo, timeout, bug), el sistema debe hacer un fallback a un comportamiento determinístico predefinido (ej. un mensaje de "no disponible"), garantizando la continuidad operacional.

## Configuración Separada

Para garantizar el aislamiento, la configuración de cada instancia de Hermes se gestiona de forma independiente.

-   **Hermes de Factoría:** Utiliza su propia configuración (no documentada aquí).
-   **Hermes de Producto:** Se configura mediante una variable de entorno que apunta a un archivo de configuración YAML específico:

    ```bash
    HERMES_PRODUCT_CONFIG_PATH=/path/to/your/hermes_product_config.yaml
    ```

Este archivo define el modelo a usar, el system prompt y, más importante, la **lista blanca de herramientas permitidas** para la instancia de producto, previniendo la escalada de privilegios.
