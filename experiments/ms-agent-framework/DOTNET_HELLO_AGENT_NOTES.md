# Microsoft Agent Framework — notas del sample .NET 01_hello_agent

## Fuente revisada

Sample oficial:

```text
microsoft/agent-framework/dotnet/samples/01-get-started/01_hello_agent
```

Archivos principales:

```text
Program.cs
01_hello_agent.csproj
```

## Qué demuestra el sample

El sample crea un agente simple usando:

```text
Azure OpenAI
DefaultAzureCredential
Microsoft.Agents.AI
Azure.AI.OpenAI
OpenAI.Chat
```

Flujo conceptual:

```text
AZURE_OPENAI_ENDPOINT
+ AZURE_OPENAI_DEPLOYMENT_NAME
+ DefaultAzureCredential
→ AzureOpenAIClient
→ ChatClient
→ AsAIAgent(...)
→ RunAsync(...)
→ RunStreamingAsync(...)
```

## Variables requeridas por el sample

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME
```

El deployment default del sample es:

```text
gpt-5.4-mini
```

## Riesgo para SmartPyme

Este sample es útil para entender el patrón, pero todavía no debe tocar SmartPyme productivo porque:

```text
- requiere Azure OpenAI configurado;
- usa credenciales de Azure;
- llama LLM;
- no prueba todavía workflow graph;
- no resuelve aún el problema de producción de código por fases.
```

## Decisión para la factoría

Para SmartPyme, el orden correcto sigue siendo:

```text
1. mantener hello_workflow.py determinístico sin LLM;
2. instalar framework en venv aislado;
3. probar import real del paquete;
4. crear un workflow graph sin LLM;
5. recién después evaluar un agente con LLM;
6. no usar Azure/OpenAI credentials hasta tener grafo estable.
```

## Próximo hito propuesto

```text
HITO_MS_AF_01_IMPORT_AND_GRAPH_NO_LLM
```

Objetivo:

```text
Verificar import real de agent_framework y modelar un grafo mínimo sin llamadas LLM.
```

Criterio de éxito:

```text
- venv aislado instala agent-framework;
- import agent_framework funciona;
- workflow local sigue devolviendo PASS;
- no se modifica app/**;
- no se toca Hermes;
- no se usan credenciales Azure;
- no se llama LLM.
```
