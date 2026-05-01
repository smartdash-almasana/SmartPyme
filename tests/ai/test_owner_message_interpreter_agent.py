from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ai.agents import owner_message_interpreter_agent as agent_module
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation


_API_KEYS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
)


def _clear_api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _API_KEYS:
        monkeypatch.delenv(key, raising=False)


class _SuccessfulFakeAgent:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    async def run(self, prompt: str):
        return SimpleNamespace(
            output=OwnerMessageInterpretation(
                intent="consultar_ventas",
                entities=["ventas"],
                variables=["monto"],
                evidence=["planilla mencionada"],
                doubts=["periodo no especificado"],
                confidence=0.8,
            )
        )


class _FailingFakeAgent:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def run(self, prompt: str):
        raise RuntimeError("llm failed")


class _InvalidFakeAgent:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def run(self, prompt: str):
        return SimpleNamespace(output={"intent": "x", "unexpected": "not allowed"})


def test_returns_none_when_pydantic_ai_is_not_available(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(agent_module, "_load_agent_class", lambda: None)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    result = agent_module.interpret_owner_message_with_ai("Revisame las ventas")

    assert result is None


def test_returns_none_without_api_key(monkeypatch: pytest.MonkeyPatch):
    _clear_api_keys(monkeypatch)
    monkeypatch.setattr(agent_module, "_load_agent_class", lambda: _SuccessfulFakeAgent)

    result = agent_module.interpret_owner_message_with_ai("Revisame las ventas")

    assert result is None


def test_successful_agent_run_returns_validated_interpretation(monkeypatch: pytest.MonkeyPatch):
    _clear_api_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(agent_module, "_load_agent_class", lambda: _SuccessfulFakeAgent)

    result = agent_module.interpret_owner_message_with_ai("Revisame las ventas")

    assert isinstance(result, OwnerMessageInterpretation)
    assert result.intent == "consultar_ventas"
    assert result.entities == ["ventas"]
    assert result.variables == ["monto"]
    assert result.evidence == ["planilla mencionada"]
    assert result.doubts == ["periodo no especificado"]
    assert result.confidence == 0.8


def test_agent_run_exception_returns_none(monkeypatch: pytest.MonkeyPatch):
    _clear_api_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(agent_module, "_load_agent_class", lambda: _FailingFakeAgent)

    result = agent_module.interpret_owner_message_with_ai("Revisame las ventas")

    assert result is None


def test_invalid_agent_output_returns_none(monkeypatch: pytest.MonkeyPatch):
    _clear_api_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(agent_module, "_load_agent_class", lambda: _InvalidFakeAgent)

    result = agent_module.interpret_owner_message_with_ai("Revisame las ventas")

    assert result is None


def test_empty_message_returns_none(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(agent_module, "_load_agent_class", lambda: _SuccessfulFakeAgent)

    result = agent_module.interpret_owner_message_with_ai("   ")

    assert result is None
