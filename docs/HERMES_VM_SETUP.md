# Hermes VM setup

## HERMES_REPO_PATH

`HermesSmartPymeRuntime` carga Hermes desde una ruta explicita para evitar conflictos con modulos locales de SmartPyme.

Linux VM:

```bash
export HERMES_REPO_PATH=/data/repos/hermes-agent
```

Windows PowerShell:

```powershell
$env:HERMES_REPO_PATH="E:\BuenosPasos\smartbridge\hermes-agent"
```

Los smokes de import solo cargan `AIAgent` con:

```python
from run_agent import AIAgent
```

No instancian Hermes, no llaman LLM y no usan tools externas.
