import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from factory.agent_min import vertex_entrypoint
from factory.agent_min.agent import AgentMin
from factory.agent_min.config import AgentMinConfig, load_agent_min_config


def test_load_config_fails_when_service_url_missing(monkeypatch):
    monkeypatch.delenv("SERVICE_URL", raising=False)
    monkeypatch.setenv("INVOKER_SA", "agent@example.iam.gserviceaccount.com")

    with pytest.raises(ValueError, match="Missing required config: SERVICE_URL"):
        load_agent_min_config()


def test_load_config_fails_when_invoker_sa_missing(monkeypatch):
    monkeypatch.setenv("SERVICE_URL", "https://code-writer-api-123.a.run.app")
    monkeypatch.delenv("INVOKER_SA", raising=False)

    with pytest.raises(ValueError, match="Missing required config: INVOKER_SA"):
        load_agent_min_config()


def test_load_config_success_from_env(monkeypatch):
    monkeypatch.setenv("SERVICE_URL", "https://code-writer-api-123.a.run.app")
    monkeypatch.setenv("INVOKER_SA", "agent@example.iam.gserviceaccount.com")

    config = load_agent_min_config()

    assert config == AgentMinConfig(
        service_url="https://code-writer-api-123.a.run.app",
        invoker_sa="agent@example.iam.gserviceaccount.com",
    )


def test_build_invocation_plan_returns_expected_fields():
    agent = AgentMin(
        AgentMinConfig(
            service_url="https://code-writer-api-123.a.run.app",
            invoker_sa="agent@example.iam.gserviceaccount.com",
        )
    )

    plan = agent.build_invocation_plan()

    assert plan.service_url == "https://code-writer-api-123.a.run.app"
    assert plan.invoker_sa == "agent@example.iam.gserviceaccount.com"
    assert plan.auth_mode == "OIDC ID token (Bearer)"
    assert plan.endpoint_hint == "POST /write-file-sandbox"


def test_vertex_entrypoint_is_importable():
    assert callable(vertex_entrypoint)
