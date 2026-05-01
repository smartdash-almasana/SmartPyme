from collections.abc import Callable
from typing import Any

Executor = Callable[[dict[str, Any]], dict[str, Any]]


def execute_echo(payload: dict[str, Any]) -> dict[str, Any]:
    return {"echoed_message": payload["message"]}


def execute_wrap_echo(payload: dict[str, Any]) -> dict[str, Any]:
    return {"final_message": f"wrapped: {payload['echoed_message']}"}


def execute_invalid_output(_: dict[str, Any]) -> dict[str, Any]:
    return {"wrong": "shape"}


EXECUTOR_MAP: dict[str, Executor] = {
    "builtin.echo": execute_echo,
    "builtin.wrap_echo": execute_wrap_echo,
    "builtin.invalid_output": execute_invalid_output,
}


def get_executor(executor_ref: str) -> Executor:
    executor = EXECUTOR_MAP.get(executor_ref)
    if executor is None:
        raise ValueError(f"Executor not found: {executor_ref}")
    return executor
