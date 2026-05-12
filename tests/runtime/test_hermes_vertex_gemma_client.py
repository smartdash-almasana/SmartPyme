from __future__ import annotations

import sys
from types import ModuleType

from app.runtime.hermes_vertex_gemma_client import VertexGemmaClient

BASE_CONFIG = {
    "system_prompt": "prompt clínico",
    "model": {
        "default": "gemma-4",
        "provider_model_id": "google/gemma-4-26b-a4b-it-maas@001",
        "temperature": 0.1,
        "max_output_tokens": 800,
    },
    "vertex": {
        "enabled": True,
        "project_id_env": "GOOGLE_CLOUD_PROJECT",
        "location_env": "VERTEX_LOCATION",
        "model_id_env": "HERMES_PRODUCT_VERTEX_MODEL_ID",
        "model_id": "google/gemma-4-26b-a4b-it-maas@001",
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


def test_resolve_vertex_settings_uses_confirmed_model_and_generation_kwargs(monkeypatch):
    _set_vertex_env(monkeypatch)
    client = VertexGemmaClient()

    settings = client._resolve_vertex_settings(BASE_CONFIG)

    assert settings == {
        "project_id": "smartseller-490511",
        "location": "us-central1",
        "model_id": "google/gemma-4-26b-a4b-it-maas@001",
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
    monkeypatch.setitem(sys.modules, "vertexai", None)
    client = VertexGemmaClient()

    response = client._invoke_vertex(
        "prompt",
        {
            "project_id": "smartseller-490511",
            "location": "us-central1",
            "model_id": "google/gemma-4-26b-a4b-it-maas@001",
            "model_kwargs": {},
        },
    )

    assert response is None


def test_invoke_vertex_returns_none_on_vertex_exception(monkeypatch):
    vertexai = ModuleType("vertexai")
    vertexai.init = lambda **kwargs: None

    generative_models = ModuleType("vertexai.generative_models")

    class FailingModel:
        def __init__(self, model_id: str) -> None:
            self.model_id = model_id

        def generate_content(self, prompt: str, generation_config: object) -> object:
            raise RuntimeError("vertex failure")

    class GenerationConfig:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    generative_models.GenerativeModel = FailingModel
    generative_models.GenerationConfig = GenerationConfig
    monkeypatch.setitem(sys.modules, "vertexai", vertexai)
    monkeypatch.setitem(sys.modules, "vertexai.generative_models", generative_models)

    client = VertexGemmaClient()
    response = client._invoke_vertex(
        "prompt",
        {
            "project_id": "smartseller-490511",
            "location": "us-central1",
            "model_id": "google/gemma-4-26b-a4b-it-maas@001",
            "model_kwargs": {"temperature": 0.1, "max_output_tokens": 800},
        },
    )

    assert response is None


def test_invoke_vertex_returns_fake_response_and_passes_generation_kwargs(monkeypatch):
    captured: dict = {}
    vertexai = ModuleType("vertexai")

    def fake_init(**kwargs: object) -> None:
        captured["init"] = kwargs

    vertexai.init = fake_init
    generative_models = ModuleType("vertexai.generative_models")

    class FakeResponse:
        text = " respuesta vertex "

    class FakeModel:
        def __init__(self, model_id: str) -> None:
            captured["model_id"] = model_id

        def generate_content(self, prompt: str, generation_config: object) -> object:
            captured["prompt"] = prompt
            captured["generation_config"] = generation_config
            return FakeResponse()

    class GenerationConfig:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    generative_models.GenerativeModel = FakeModel
    generative_models.GenerationConfig = GenerationConfig
    monkeypatch.setitem(sys.modules, "vertexai", vertexai)
    monkeypatch.setitem(sys.modules, "vertexai.generative_models", generative_models)

    client = VertexGemmaClient()
    response = client._invoke_vertex(
        "prompt completo",
        {
            "project_id": "smartseller-490511",
            "location": "us-central1",
            "model_id": "google/gemma-4-26b-a4b-it-maas@001",
            "model_kwargs": {"temperature": 0.1, "max_output_tokens": 800},
        },
    )

    assert response == "respuesta vertex"
    assert captured["init"] == {"project": "smartseller-490511", "location": "us-central1"}
    assert captured["model_id"] == "google/gemma-4-26b-a4b-it-maas@001"
    assert captured["prompt"] == "prompt completo"
    assert captured["generation_config"].kwargs == {
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
