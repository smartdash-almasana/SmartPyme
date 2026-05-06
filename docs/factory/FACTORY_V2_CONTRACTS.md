# Factory V2 Contracts

Documento canónico de contratos actuales de `factory_v2`.

`factory_v2` es una POC determinística de bajo costo para ejecutar un flujo mínimo de factoría:

```text
audit → implement → sandbox → review
```

El flujo principal no depende de LLMs. Cada nodo produce evidencia local y el cierre de ejecución queda resumido en `run.json`.

---

## Principios de diseño

- **Mínimo suficiente**: los contratos contienen solo lo necesario para la POC actual.
- **Determinístico**: el grafo ejecuta lógica Python pura y predecible.
- **Auditable**: cada nodo genera un `ExecutionResultV2` persistible como JSON.
- **Sandbox inyectable**: el grafo acepta un adapter opcional; por defecto usa `FakeSandboxAdapter`.
- **No legacy como base**: `factory_v2` puede reutilizar piezas validadas, pero no debe mezclar su ciclo activo con `factory/core` ni `queue_runner.py`.

---

## Archivos fuente

```text
factory_v2/contracts.py
factory_v2/graph.py
factory_v2/evidence.py
factory_v2/sandbox.py
tests/factory_v2/
```

---

## Contratos Pydantic

### `NodeStatus`

Enum de estado para nodos del grafo.

```python
class NodeStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
```

Semántica:

| Estado | Uso |
|---|---|
| `PASS` | El nodo terminó correctamente. |
| `FAIL` | El nodo ejecutó pero falló. |
| `BLOCKED` | El nodo no puede avanzar por una condición bloqueante. |

---

### `TaskSpecV2`

Especificación mínima de entrada para una ejecución del grafo.

```python
class TaskSpecV2(BaseModel):
    task_id: str
    objective: str
    files_allowed: List[str] = Field(default_factory=list)
    files_forbidden: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    modo: str = "AUDIT_ONLY"
```

Campos:

| Campo | Tipo | Semántica |
|---|---|---|
| `task_id` | `str` | Identificador único de tarea. |
| `objective` | `str` | Objetivo en una línea. |
| `files_allowed` | `list[str]` | Rutas permitidas para el ciclo. |
| `files_forbidden` | `list[str]` | Rutas prohibidas. |
| `acceptance_criteria` | `list[str]` | Criterios de aceptación declarados. |
| `modo` | `str` | `AUDIT_ONLY` o `WRITE_AUTHORIZED`; default `AUDIT_ONLY`. |

Regla actual:

- Si `task_id` u `objective` están vacíos, el nodo `audit` devuelve `BLOCKED`, marca `halted=True` y usa `halt_reason="BLOCKED_MISSING_REQUIRED_FIELDS"`.

---

### `ExecutionResultV2`

Resultado de ejecución de un nodo individual.

```python
class ExecutionResultV2(BaseModel):
    task_id: str
    node_name: str
    status: NodeStatus
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    evidence_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reasons: List[str] = Field(default_factory=list)
```

Campos:

| Campo | Tipo | Semántica |
|---|---|---|
| `task_id` | `str` | Tarea asociada. |
| `node_name` | `str` | Nodo productor: `audit`, `implement`, `sandbox`, `review`. |
| `status` | `NodeStatus` | Resultado semántico del nodo. |
| `stdout` | `str` | Salida estándar o resumen útil. |
| `stderr` | `str` | Error o causa técnica. |
| `return_code` | `int` | Código de retorno técnico. |
| `evidence_path` | `str | None` | Ruta del JSON de evidencia escrito. |
| `timestamp` | `datetime` | Fecha/hora UTC autogenerada. |
| `reasons` | `list[str]` | Razones adicionales de fallo/bloqueo, especialmente desde sandbox. |

---

### `GraphState`

Estado compartido que fluye por el grafo.

```python
class GraphState(BaseModel):
    task_spec: TaskSpecV2
    audit_result: Optional[ExecutionResultV2] = None
    implement_result: Optional[ExecutionResultV2] = None
    sandbox_result: Optional[ExecutionResultV2] = None
    review_result: Optional[ExecutionResultV2] = None
    generated_code: str = ""
    test_code: str = ""
    halted: bool = False
    halt_reason: str = ""
```

Campos clave:

| Campo | Semántica |
|---|---|
| `task_spec` | Entrada original de la ejecución. |
| `audit_result` | Resultado del nodo de auditoría. |
| `implement_result` | Resultado del nodo de implementación stub. |
| `sandbox_result` | Resultado de sandbox. |
| `review_result` | Resultado de revisión final. |
| `generated_code` | Código stub generado por `implement`. |
| `test_code` | Test stub generado por `implement`. |
| `halted` | Indica corte temprano del flujo. |
| `halt_reason` | Motivo del corte temprano. |

---

## EvidenceWriter

Archivo fuente: `factory_v2/evidence.py`.

`EvidenceWriter` escribe evidencia JSON local bajo:

```text
factory_v2/evidence/<task_id>/
```

### `EvidenceWriter.write`

Firma actual:

```python
def write(self, result: ExecutionResultV2) -> Path:
```

Contrato:

- Recibe un `ExecutionResultV2`.
- Crea el directorio `evidence/<task_id>/` si no existe.
- Escribe un JSON por nodo.
- Devuelve la ruta escrita.

Nombre de archivo:

```text
<node_name>_<timestamp_utc>.json
```

Ejemplo:

```text
factory_v2/evidence/TASK_001/audit_20260506T120000Z.json
```

Contenido:

- Serialización `model_dump_json(indent=2)` del `ExecutionResultV2`.

---

### `EvidenceWriter.write_run`

Firma actual:

```python
def write_run(self, task_id: str, payload: dict) -> Path:
```

Contrato:

- Recibe `task_id` y un `payload` de resumen.
- Crea el directorio `evidence/<task_id>/` si no existe.
- Escribe `run.json`.
- Devuelve la ruta escrita.

Ruta esperada:

```text
factory_v2/evidence/<task_id>/run.json
```

Contenido:

- JSON con `indent=2` y `ensure_ascii=False`.

---

## `run.json` payload

El payload se arma en `_write_run_evidence` dentro de `factory_v2/graph.py`.

Estructura actual:

```json
{
  "task_id": "TASK_001",
  "status": "PASS",
  "halted": false,
  "halt_reason": null,
  "nodes": {
    "audit_result": "PASS",
    "implement_result": "PASS",
    "sandbox_result": "PASS",
    "review_result": "PASS"
  }
}
```

Campos:

| Campo | Tipo | Semántica |
|---|---|---|
| `task_id` | `str` | Tarea ejecutada. |
| `status` | `str` | Estado global: `PASS`, `FAIL` o `BLOCKED`. |
| `halted` | `bool` | Si el grafo se detuvo antes del final. |
| `halt_reason` | `str | None` | Motivo de corte temprano o `None`. |
| `nodes` | `dict` | Mapa de resultados por atributo de nodo. |

Regla de estado global:

- Si `state.halted` es `True`, `status="BLOCKED"`.
- Si `review_result` existe y no es `PASS`, `status="FAIL"`.
- En cualquier otro caso exitoso, `status="PASS"`.

---

## SandboxAdapterProtocol

Archivo fuente: `factory_v2/graph.py`.

Protocolo mínimo que debe cumplir cualquier sandbox inyectado en `run_graph`.

```python
class SandboxAdapterProtocol(Protocol):
    def execute(self, task_id: str, code: str, test_code: str) -> ExecutionResultV2: ...
```

Contrato:

- Recibe `task_id`, `code` y `test_code`.
- Devuelve siempre un `ExecutionResultV2`.
- No debe devolver estructuras legacy al grafo.
- El grafo no conoce si el adapter es fake, mock o Docker real.

---

## FakeSandboxAdapter

Archivo fuente: `factory_v2/sandbox.py`.

Adapter por defecto de `factory_v2`.

Contrato actual:

- Siempre devuelve `ExecutionResultV2(status=PASS)`.
- No ejecuta Docker real.
- Inserta en `stdout` un resumen con longitud de código/test y prefijo del contenido combinado.
- Sirve para POC determinística y tests rápidos.

Uso implícito:

```python
adapter: SandboxAdapterProtocol = sandbox_adapter or FakeSandboxAdapter()
```

Implicancia:

- Si `run_graph` no recibe adapter explícito, no usa Docker.
- Docker real no queda habilitado como default global.

---

## DockerSandboxAdapter

Archivo fuente: `factory_v2/sandbox.py`.

Adapter real opcional que envuelve `DockerExecutor` validado previamente.

Contrato actual:

- Construye un comando shell con `code + test_code` codificado en base64.
- Crea un `SandboxExecutionRequest` con:
  - `task_id`
  - `command`
  - `timeout_seconds`
  - `network_disabled=True`
- Ejecuta mediante `DockerExecutor`.
- Mapea `SandboxExecutionResult` a `ExecutionResultV2`.

Mapeo de estado:

| Resultado Docker | Estado factory_v2 |
|---|---|
| `blocked=True` | `NodeStatus.BLOCKED` |
| `returncode != 0` | `NodeStatus.FAIL` |
| `returncode == 0` y no bloqueado | `NodeStatus.PASS` |

Límite actual:

- Aunque el adapter existe, no debe habilitarse como default global.
- Debe usarse por inyección explícita.
- Antes de habilitarlo operativamente conviene agregar una política de comandos (`CommandPolicyV2`).

---

## Flujo normal

Entrada:

```python
run_graph(task_spec)
```

Secuencia:

```text
1. audit
2. implement
3. sandbox
4. review
5. run.json
```

Detalle:

1. `audit` valida campos mínimos.
2. `implement` genera código y test stub determinísticos.
3. `sandbox` ejecuta mediante adapter inyectado o `FakeSandboxAdapter`.
4. `review` evalúa el resultado de sandbox.
5. `_write_run_evidence` escribe `run.json`.

Evidencia esperada:

```text
factory_v2/evidence/<task_id>/audit_<timestamp>.json
factory_v2/evidence/<task_id>/implement_<timestamp>.json
factory_v2/evidence/<task_id>/sandbox_<timestamp>.json
factory_v2/evidence/<task_id>/review_<timestamp>.json
factory_v2/evidence/<task_id>/run.json
```

---

## Halt temprano

El halt temprano ocurre cuando el grafo no debe seguir ejecutando nodos posteriores.

Caso cubierto actualmente:

```text
BLOCKED_MISSING_REQUIRED_FIELDS
```

Condición:

- `task_id` vacío, o
- `objective` vacío.

Efecto:

- `audit_result.status = BLOCKED`.
- `state.halted = True`.
- `state.halt_reason = "BLOCKED_MISSING_REQUIRED_FIELDS"`.
- Se escribe evidencia de `audit`.
- Se escribe `run.json`.
- No se ejecutan `implement`, `sandbox` ni `review`.

---

## Límites actuales

`factory_v2` todavía es una POC determinística.

Límites explícitos:

- `implement` genera un stub fijo; no implementa código real de negocio.
- `FakeSandboxAdapter` siempre devuelve `PASS`.
- `DockerSandboxAdapter` existe, pero no es default.
- No hay `CommandPolicyV2` todavía.
- No hay integración con agentes reales.
- No hay integración con HITL/Hermes Runtime.
- No hay PR automation propia de `factory_v2`.
- No debe mezclarse con legacy `factory/core` ni `queue_runner.py` durante este ciclo.

---

## Regla operativa vigente

Antes de ampliar `factory_v2`, mantener ciclos cortos:

```text
1 objetivo pequeño
1 archivo o componente
1 test mínimo
PASS / PARTIAL / BLOCKED
1 siguiente paso
```

Próximo frente técnico recomendado por estado actual:

```text
CommandPolicyV2 antes de habilitar DockerSandboxAdapter operativamente.
```
