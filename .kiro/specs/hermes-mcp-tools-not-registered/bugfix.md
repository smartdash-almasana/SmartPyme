# Bugfix Requirements Document

## Introduction

MCP tools from the SmartPyme bridge (`mcp_smartpyme_bridge.py`) never appear in hermes-agent
because `discover_mcp_tools()` reads `mcp_servers` exclusively from
`~/.hermes/config.yaml` (via `hermes_cli.config.load_config`), but that file did not exist.
The `mcp_servers` block in `cli-config.yaml` is read only by `load_cli_config()` in `cli.py`
and is **never forwarded** to `_load_mcp_config()` in `tools/mcp_tool.py`.
The result is that `_load_mcp_config()` returns `{}`, `discover_mcp_tools()` exits early with
no tools registered, and no error is surfaced to the user.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN `~/.hermes/config.yaml` does not exist AND `mcp_servers` is only defined in
`cli-config.yaml` THEN `_load_mcp_config()` returns `{}` and the system registers zero MCP
tools.

1.2 WHEN `discover_mcp_tools()` is called with an empty config THEN the system logs
`"No MCP servers configured"` at DEBUG level and returns `[]` with no visible error.

1.3 WHEN hermes is run with `-q "hello" --verbose` THEN the system starts normally and
responds, but no `mcp_smartpyme_*` tools appear because `discover_mcp_tools()` found no
servers to connect to.

### Expected Behavior (Correct)

2.1 WHEN `~/.hermes/config.yaml` exists and contains a valid `mcp_servers.smartpyme` block
with `enabled: true`, `command: "C:/Python314/python.exe"`, and the correct bridge path
THEN `_load_mcp_config()` SHALL return the smartpyme server config dict.

2.2 WHEN `_load_mcp_config()` returns a non-empty dict THEN `discover_mcp_tools()` SHALL
connect to the stdio server, list its tools, and register them as
`mcp_smartpyme_<tool_name>` in the tool registry.

2.3 WHEN the bridge process is started via stdio transport THEN the system SHALL register
exactly 7 tools: `mcp_smartpyme_get_job_status`, `mcp_smartpyme_list_pending_validations`,
`mcp_smartpyme_get_evidence`, `mcp_smartpyme_list_resources`, `mcp_smartpyme_read_resource`,
`mcp_smartpyme_list_prompts`, `mcp_smartpyme_get_prompt`.

### Unchanged Behavior (Regression Prevention)

3.1 WHEN `~/.hermes/config.yaml` exists but contains no `mcp_servers` key THEN the system
SHALL CONTINUE TO start normally with zero MCP tools and no error.

3.2 WHEN `HERMES_IGNORE_USER_CONFIG=1` is set THEN the system SHALL CONTINUE TO skip
`~/.hermes/config.yaml` and fall back to `cli-config.yaml` for CLI display settings
(model, toolsets, etc.), with MCP discovery returning empty as before.

3.3 WHEN `mcp_servers.smartpyme.enabled` is `false` in `config.yaml` THEN the system
SHALL CONTINUE TO skip that server without disconnecting any existing session.

3.4 WHEN hermes is run in `-q` (single-query) mode THEN the system SHALL CONTINUE TO call
`discover_mcp_tools()` at module import time (via `model_tools.py`) before the query runs.

---

## Evidence Summary (collected during investigation)

### Real Config Path
- `get_hermes_home()` → `C:\Users\PC\.hermes` (no `HERMES_HOME` env var set)
- `get_config_path()` → `C:\Users\PC\.hermes\config.yaml`
- File **did not exist** before this fix

### Correct Python
- `C:\Python314\python.exe` — hermes-agent installed editable at
  `E:\BuenosPalos\smartbridge\hermes-agent`
  (evidence: `pip show hermes-agent` → `Editable project location: E:\BuenosPasos\smartbridge\hermes-agent`)
- `mcp` and `fastmcp` packages: **present** in `C:\Python314`
- `.venv\Scripts\python.exe` in smartbridge root: **missing** `hermes_constants` module

### Bridge Standalone Test
Command: `C:\Python314\python.exe "E:\BuenosPasos\smartbridge\SmartPyme\mcp_smartpyme_bridge.py"`
Result: process alive after 3 seconds, no stdout/stderr output → **stdio server alive**

### Root Cause (proven)
`_load_mcp_config()` in `tools/mcp_tool.py` calls `hermes_cli.config.load_config()` which
reads **only** `~/.hermes/config.yaml`. The `mcp_servers` block in `cli-config.yaml` is
consumed by `load_cli_config()` in `cli.py` for CLI settings but is **never passed** to
`_load_mcp_config()`. Since `~/.hermes/config.yaml` did not exist, `_load_mcp_config()`
returned `{}` on every call.

### Fix Applied
Created `C:\Users\PC\.hermes\config.yaml` with:
```yaml
mcp_servers:
  smartpyme:
    enabled: true
    command: "C:/Python314/python.exe"
    args:
      - "E:/BuenosPasos/smartbridge/SmartPyme/mcp_smartpyme_bridge.py"
```

### Verification
After fix, `discover_mcp_tools()` logs:
```
INFO:tools.mcp_tool:MCP server 'smartpyme' (stdio): registered 7 tool(s):
  mcp_smartpyme_get_job_status, mcp_smartpyme_list_pending_validations,
  mcp_smartpyme_get_evidence, mcp_smartpyme_list_resources,
  mcp_smartpyme_read_resource, mcp_smartpyme_list_prompts, mcp_smartpyme_get_prompt
```

---

## Bug Condition (Pseudocode)

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type HermesStartupContext
  OUTPUT: boolean

  RETURN NOT file_exists(get_hermes_home() / "config.yaml")
         OR config_yaml_has_no_mcp_servers(get_hermes_home() / "config.yaml")
END FUNCTION
```

```pascal
// Property: Fix Checking
FOR ALL X WHERE isBugCondition(X) DO
  result ← discover_mcp_tools'(X)
  ASSERT result = []   // no crash, no tools, no silent error swallowed
END FOR
```

```pascal
// Property: Preservation Checking
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT discover_mcp_tools(X) = discover_mcp_tools'(X)
END FOR
```
