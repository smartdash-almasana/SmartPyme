from __future__ import annotations

from app.runtime.hermes_vertex_gemma_client import VertexGemmaClient


def test_generate_returns_none_when_vertex_disabled(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartseller-490511")
    monkeypatch.setenv("VERTEX_LOCATION", "us-central1")
    client = VertexGemmaClient()

    response = client.generate(
        {"summary": {"text": "estado"}},
        {"vertex": {"enabled": False}},
    )

    assert response is None


def test_generate_returns_none_without_grounding(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartseller-490511")
    monkeypatch.setenv("VERTEX_LOCATION", "us-central1")
    client = VertexGemmaClient()

    response = client.generate(
        {},
        {
            "vertex": {
                "enabled": True,
                "project_id_env": "GOOGLE_CLOUD_PROJECT",
                "location_env": "VERTEX_LOCATION",
                "model_id": "google/gemma-4-26b-a4b-it-maas@001",
            }
        },
    )

    assert response is None


def test_generate_returns_none_when_project_env_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.setenv("VERTEX_LOCATION", "us-central1")
    client = VertexGemmaClient()

    response = client.generate(
        {"summary": {"text": "estado"}},
        {
            "vertex": {
                "enabled": True,
                "project_id_env": "GOOGLE_CLOUD_PROJECT",
                "location_env": "VERTEX_LOCATION",
                "model_id": "google/gemma-4-26b-a4b-it-maas@001",
            }
        },
    )

    assert response is None


def test_generate_returns_none_when_location_env_missing(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartseller-490511")
    monkeypatch.delenv("VERTEX_LOCATION", raising=False)
    client = VertexGemmaClient()

    response = client.generate(
        {"summary": {"text": "estado"}},
        {
            "vertex": {
                "enabled": True,
                "project_id_env": "GOOGLE_CLOUD_PROJECT",
                "location_env": "VERTEX_LOCATION",
                "model_id": "google/gemma-4-26b-a4b-it-maas@001",
            }
        },
    )

    assert response is None


def test_resolve_vertex_settings_uses_confirmed_model_and_generation_kwargs(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartseller-490511")
    monkeypatch.setenv("VERTEX_LOCATION", "us-central1")
    client = VertexGemmaClient()

    settings = client._resolve_vertex_settings(
        {
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
    )

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

    settings = client._resolve_vertex_settings(
        {
            "vertex": {
                "enabled": True,
                "project_id_env": "GOOGLE_CLOUD_PROJECT",
                "location_env": "VERTEX_LOCATION",
                "model_id_env": "HERMES_PRODUCT_VERTEX_MODEL_ID",
                "model_id": "yaml-model",
            }
        }
    )

    assert settings is not None
    assert settings["model_id"] == "env-model"


def test_has_required_grounding_accepts_findings():
    assert VertexGemmaClient._has_required_grounding(
        {"findings": [{"finding_type": "VENTA_BAJO_COSTO"}]}
    )
