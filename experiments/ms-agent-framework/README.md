# Microsoft Agent Framework Sandbox

## Propósito

Sandbox aislado para evaluar Microsoft Agent Framework como motor de workflow explícito para SmartPyme Factory.

Este experimento no reemplaza Hermes ni modifica el runtime productivo de SmartPyme.

## Decisión de arquitectura

```text
GitHub = fuente de verdad
Hermes = canal operativo / Telegram / ejecutor auxiliar en VM
Microsoft Agent Framework = motor experimental de workflow explícito
GPT = arquitecto y auditor
Kiro/Codex/DeepSeek = workers acotados
```

## Alcance del sandbox

Permitido:

```text
- instalar dependencias en venv local;
- ejecutar workflows sin LLM;
- validar contratos JSON;
- probar pasos Planner → Validator → PublisherMock;
- documentar resultados.
```

Prohibido:

```text
- modificar app/**;
- tocar factory/core/** productivo;
- tocar servicios systemd;
- tocar .env productivos;
- reemplazar Hermes;
- ejecutar tareas reales de SmartPyme desde este sandbox.
```

## Instalación recomendada en VM

Ruta externa sugerida:

```bash
mkdir -p /opt/smartpyme-factory/experiments/ms-agent-framework
cd /opt/smartpyme-factory/experiments/ms-agent-framework

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r /opt/smartpyme-factory/repos/SmartPyme/experiments/ms-agent-framework/requirements.txt
```

## Smoke test sin LLM

Desde el repo SmartPyme:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
PYTHONPATH=. python3 experiments/ms-agent-framework/hello_workflow.py
```

Salida esperada:

```json
{
  "workflow_id": "ms_af_sandbox_v1",
  "status": "PASS",
  "steps": [
    "planner_mock",
    "validator_mock",
    "publisher_mock"
  ]
}
```

## Criterio de éxito

El sandbox sirve si demuestra que podemos representar el flujo como pasos explícitos, sin prompts largos y sin que un agente tenga que redescubrir arquitectura.

## Próximo hito si pasa

```text
HITO_MS_AF_01_WORKFLOW_GRAPH_HELLO
```

Objetivo: reemplazar el mock secuencial por un workflow graph real del framework, todavía sin LLM.
