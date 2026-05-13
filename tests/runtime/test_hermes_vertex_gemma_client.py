from __future__ import annotations

import sys
from types import ModuleType

from app.runtime.hermes_vertex_gemma_client import VertexGemmaClient

BASE_CONFIG = {
    "system_prompt": "prompt clínico",
    "model": {
        "default": "gemma-4",
        "provider_model_id": "google/gemma-4-26b-a4b-it-maas@001",
        "runtime_model_id": "gemma-4-26b-a4b-it-maas",
        "temperature": 0.1,
        "max_output_tokens": 800,
    },
    "vertex": {
        "enabled": True,
        "project_id_env": "GOOGLE_CLOUD_PROJECT",
        "location_env": "VERTEX_LOCATION",
        "model_id_env": "HERMES_PRODUCT_VERTEX_MODEL_ID",
        "model_id": "gemma-4-26b-a4b-it-maas",
    },
}


def _payload() -> dict:
    return {
        "user_message": "explicame el finding",
        "summary": {"text": "estado"},
        "findings": [{"finding_type": "VENTA_BAJO_COSTO"}],
        "operational_report": {"risk_level": "alto"},
    }


def _set_vertex_env(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartseller-490511")
    monkeypatch.setenv("VERTEX_LOCATION", "us-central1")
    monkeypatch.delenv("HERMES_PRODUCT_VERTEX_MODEL_ID", raising=False)


def _install_fake_genai_modules(
    monkeypatch,
    fake_genai: ModuleType,
    fake_types: ModuleType,
) -> None:
    google_module = sys.modules.get("google") or ModuleType("google")
    google_module.genai = fake_genai
    fake_genai.types = fake_types
    monkeypatch.setitem(sys.modules, "google", google_module)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)


def test_generate_returns_none_when_vertex_disabled(monkeypatch):
    _set_vertex_env(monkeypatch)
    client = VertexGemmaClient()

    response = client.generate(
        {"summary": {"text": "estado"}},
        {"vertex": {"enabled": False}},
    )

    assert response is None


def test_generate_returns_none_without_grounding(monkeypatch):
    _set_vertex_env(monkeypatch)
    client = VertexGemmaClient()

    response = client.generate({}, BASE_CONFIG)

    assert response is None


def test_generate_returns_none_when_project_env_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.setenv("VERTEX_LOCATION", "us-central1")
    client = VertexGemmaClient()

    response = client.generate(_payload(), BASE_CONFIG)

    assert response is None


def test_generate_returns_none_when_location_env_missing(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartseller-490511")
    monkeypatch.delenv("VERTEX_LOCATION", raising=False)
    client = VertexGemmaClient()

    response = client.generate(_payload(), BASE_CONFIG)

    assert response is None


def test_generate_returns_none_when_user_message_missing(monkeypatch):
    _set_vertex_env(monkeypatch)
    client = VertexGemmaClient()
    payload = _payload()
    payload["user_message"] = ""

    response = client.generate(payload, BASE_CONFIG)

    assert response is None


def test_resolve_vertex_settings_uses_runtime_model_and_generation_kwargs(monkeypatch):
    _set_vertex_env(monkeypatch)
    client = VertexGemmaClient()

    settings = client._resolve_vertex_settings(BASE_CONFIG)

    assert settings == {
        "project_id": "smartseller-490511",
        "location": "us-central1",
        "model_id": "gemma-4-26b-a4b-it-maas",
        "system_prompt": "prompt clínico",
        "model_kwargs": {"temperature": 0.1, "max_output_tokens": 800},
    }


def test_resolve_vertex_settings_prefers_model_id_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartseller-490511")
    monkeypatch.setenv("VERTEX_LOCATION", "us-central1")
    monkeypatch.setenv("HERMES_PRODUCT_VERTEX_MODEL_ID", "env-model")
    client = VertexGemmaClient()

    settings = client._resolve_vertex_settings(BASE_CONFIG)

    assert settings is not None
    assert settings["model_id"] == "env-model"


def test_has_required_grounding_accepts_findings():
    assert VertexGemmaClient._has_required_grounding(
        {"findings": [{"finding_type": "VENTA_BAJO_COSTO"}]}
    )


def test_build_prompt_includes_system_user_and_grounding():
    prompt = VertexGemmaClient._build_prompt(_payload(), "prompt clínico")

    assert prompt is not None
    assert "<system>" in prompt
    assert "prompt clínico" in prompt
    assert "<user>" in prompt
    assert "explicame el finding" in prompt
    assert "<grounding>" in prompt
    assert "VENTA_BAJO_COSTO" in prompt
    assert "risk_level" in prompt


def test_invoke_vertex_returns_none_when_sdk_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "google.genai", None)
    client = VertexGemmaClient()

    response = client._invoke_vertex(
        "prompt",
        {
            "project_id": "smartseller-490511",
            "location": "us-central1",
            "model_id": "gemma-4-26b-a4b-it-maas",
            "model_kwargs": {},
        },
    )

    assert response is None


def test_invoke_vertex_returns_none_on_vertex_exception(monkeypatch):
    fake_genai = ModuleType("google.genai")
    fake_types = ModuleType("google.genai.types")

    class FailingModels:
        def generate_content(self, **kwargs: object) -> object:
            raise RuntimeError("vertex failure")

    class Client:
        def __init__(self, **kwargs: object) -> None:
            self.models = FailingModels()

    class GenerateContentConfig:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    fake_genai.Client = Client
    fake_types.GenerateContentConfig = GenerateContentConfig
    _install_fake_genai_modules(monkeypatch, fake_genai, fake_types)

    client = VertexGemmaClient()
    response = client._invoke_vertex(
        "prompt",
        {
            "project_id": "smartseller-490511",
            "location": "us-central1",
            "model_id": "gemma-4-26b-a4b-it-maas",
            "model_kwargs": {"temperature": 0.1, "max_output_tokens": 800},
        },
    )

    assert response is None


def test_invoke_vertex_returns_fake_response_and_passes_generation_kwargs(monkeypatch):
    captured: dict = {}
    fake_genai = ModuleType("google.genai")
    fake_types = ModuleType("google.genai.types")

    class FakeResponse:
        text = " respuesta vertex "

    class FakeModels:
        def generate_content(self, **kwargs: object) -> object:
            captured["generate_content"] = kwargs
            return FakeResponse()

    class Client:
        def __init__(self, **kwargs: object) -> None:
            captured["client"] = kwargs
            self.models = FakeModels()

    class GenerateContentConfig:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    fake_genai.Client = Client
    fake_types.GenerateContentConfig = GenerateContentConfig
    _install_fake_genai_modules(monkeypatch, fake_genai, fake_types)

    client = VertexGemmaClient()
    response = client._invoke_vertex(
        "prompt completo",
        {
            "project_id": "smartseller-490511",
            "location": "us-central1",
            "model_id": "gemma-4-26b-a4b-it-maas",
            "model_kwargs": {"temperature": 0.1, "max_output_tokens": 800},
        },
    )

    assert response == "respuesta vertex"
    assert captured["client"] == {
        "vertexai": True,
        "project": "smartseller-490511",
        "location": "us-central1",
    }
    assert captured["generate_content"]["model"] == "gemma-4-26b-a4b-it-maas"
    assert captured["generate_content"]["contents"] == "prompt completo"
    assert captured["generate_content"]["config"].kwargs == {
        "temperature": 0.1,
        "max_output_tokens": 800,
    }


def test_generate_uses_vertex_fake_path(monkeypatch):
    _set_vertex_env(monkeypatch)
    captured: dict = {}

    def fake_invoke(prompt: str, settings: dict) -> str:
        captured["prompt"] = prompt
        captured["settings"] = settings
        return "respuesta generada"

    client = VertexGemmaClient()
    monkeypatch.setattr(client, "_invoke_vertex", fake_invoke)

    response = client.generate(_payload(), BASE_CONFIG)

    assert response == "respuesta generada"
    assert "prompt clínico" in captured["prompt"]
    assert "VENTA_BAJO_COSTO" in captured["prompt"]
    assert captured["settings"]["model_kwargs"] == {
        "temperature": 0.1,
        "max_output_tokens": 800,
    }
