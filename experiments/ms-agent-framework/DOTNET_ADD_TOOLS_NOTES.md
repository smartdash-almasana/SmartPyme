# Microsoft Agent Framework — notas del sample .NET 02_add_tools

## Fuente revisada

Sample oficial:

```text
microsoft/agent-framework/dotnet/samples/01-get-started/02_add_tools
```

Archivos principales:

```text
Program.cs
02_add_tools.csproj
```

## Qué demuestra el sample

El sample muestra cómo agregar herramientas de función a un agente conversacional.

Patrón central:

```text
función normal del lenguaje
+ descripción semántica
+ AIFunctionFactory.Create(func)
+ AsAIAgent(..., tools=[...])
→ el agente puede invocar la herramienta durante RunAsync / RunStreamingAsync
```

## Ejemplo conceptual del sample

El sample define una función:

```text
GetWeather(location: string) -> string
```

Y la registra como herramienta del agente:

```text
tools: [AIFunctionFactory.Create(GetWeather)]
```

Luego consulta:

```text
What is the weather like in Amsterdam?
```

El agente decide usar la herramienta para responder.

## Dependencias y runtime

El sample usa:

```text
AzureOpenAIClient
DefaultAzureCredential
Microsoft.Agents.AI
Microsoft.Extensions.AI
OpenAI.Chat
```

Variables:

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME
```

Deployment default observado:

```text
gpt-5.4-mini
```

## Lectura arquitectónica para SmartPyme

Este sample NO es todavía el workflow de producción de código.

Es un patrón para una capa distinta:

```text
Agent + Tools
```

No:

```text
Workflow graph completo
```

Diferencia crítica:

```text
Tool = capacidad invocable por un agente.
Workflow = orden explícito de pasos.
```

## Aplicación futura en SmartPyme

El patrón de tools sirve para encapsular capacidades acotadas, por ejemplo:

```text
- leer HitoSpec;
- validar HitoSpec;
- generar TaskSpec desde HitoSpec;
- correr py_compile;
- correr pytest acotado;
- correr ruff check;
- consultar git status;
- generar resumen de evidencia;
- verificar remote sync.
```

Cada herramienta debe ser determinística, limitada y auditable.

## Regla de diseño

```text
Si una acción puede ser una función determinística, debe ser tool/función, no razonamiento libre del agente.
```

Esto coincide con el objetivo de SmartPyme Factory:

```text
menos prompt largo,
más funciones pequeñas,
más JSON,
más Pydantic,
más validación mecánica.
```

## Riesgo

No conviene saltar ahora a agentes con tools y LLM porque:

```text
- requiere credenciales Azure/OpenAI;
- vuelve a introducir decisión libre del modelo;
- puede ocultar errores del workflow detrás del agente;
- todavía estamos validando el grafo sin LLM.
```

## Decisión operativa

Orden recomendado:

```text
1. cerrar graph_workflow.py real sin LLM;
2. corregir propagación planner → validator → publisher;
3. crear tools determinísticas locales sin LLM;
4. recién después montar agente con tools;
5. mantener Hermes fuera de este sandbox.
```

## Próximo hito sugerido

```text
HITO_MS_AF_03_LOCAL_TOOLS_NO_LLM
```

Objetivo:

```text
Crear funciones tipo tool determinísticas para SmartPyme Factory sin conectarlas todavía a un agente LLM.
```

Tools candidatas:

```text
load_workflow_spec(path)
validate_workflow_spec(spec)
load_hito_spec(hito_id)
generate_taskspec_preview(hito_spec)
run_smoke_validation(command)
```

Criterio de éxito:

```text
- tools ejecutan sin LLM;
- entradas/salidas son Pydantic;
- output JSON;
- no se toca app/**;
- no se toca factory/core/** productivo;
- no se toca Hermes;
- no se usan credenciales.
```
