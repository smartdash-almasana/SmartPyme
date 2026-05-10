import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from factory.agent_min.agent import AgentMin, InvocationResult, vertex_entrypoint
from factory.agent_min.config import AgentMinConfig


def test_invoke_write_file_sandbox_builds_request_and_parses_response():
    config = AgentMinConfig(
        service_url="https://code-writer-api-123.a.run.app/",
        invoker_sa="agent@example.iam.gserviceaccount.com",
    )
    agent = AgentMin(config)

    captured = {}

    def fake_token_provider(audience: str) -> str:
        captured["audience"] = audience
        return "fake-id-token"

    def fake_http_post(url, payload, headers, timeout_seconds):
        captured["url"] = url
        captured["payload"] = payload
        captured["headers"] = headers
        captured["timeout_seconds"] = timeout_seconds
        return 200, {"status": "success", "bytes_written": 42}

    result = agent.invoke_write_file_sandbox(
        owner="acme",
        repo="smartpyme",
        path="tmp/test.txt",
        content="hello",
        commit_message="test commit",
        token_provider=fake_token_provider,
        http_post=fake_http_post,
    )

    assert captured["audience"] == "https://code-writer-api-123.a.run.app/"
    assert captured["url"] == "https://code-writer-api-123.a.run.app/write-file-sandbox"
    assert captured["headers"]["Authorization"] == "Bearer fake-id-token"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["timeout_seconds"] == 15.0
    assert captured["payload"] == {
        "owner": "acme",
        "repo": "smartpyme",
        "path": "tmp/test.txt",
        "content": "hello",
        "commit_message": "test commit",
    }

    assert result.status_code == 200
    assert result.ok is True
    assert result.response_json == {"status": "success", "bytes_written": 42}


def test_invoke_write_file_sandbox_handles_non_2xx_response():
    config = AgentMinConfig(
        service_url="https://code-writer-api-123.a.run.app",
        invoker_sa="agent@example.iam.gserviceaccount.com",
    )
    agent = AgentMin(config)

    def fake_token_provider(audience: str) -> str:
        return "fake-id-token"

    def fake_http_post(url, payload, headers, timeout_seconds):
        return 403, {"detail": "Forbidden"}

    result = agent.invoke_write_file_sandbox(
        owner="acme",
        repo="smartpyme",
        path="tmp/test.txt",
        content="hello",
        commit_message="test commit",
        token_provider=fake_token_provider,
        http_post=fake_http_post,
    )

    assert result.status_code == 403
    assert result.ok is False
    assert result.response_json == {"detail": "Forbidden"}


def test_invoke_write_file_sandbox_emits_structured_logs(caplog):
    config = AgentMinConfig(
        service_url="https://code-writer-api-123.a.run.app",
        invoker_sa="agent@example.iam.gserviceaccount.com",
    )
    agent = AgentMin(config)

    def fake_token_provider(audience: str) -> str:
        return "fake-id-token"

    def fake_http_post(url, payload, headers, timeout_seconds):
        return 200, {"status": "success"}

    caplog.set_level(logging.INFO)
    agent.invoke_write_file_sandbox(
        owner="acme",
        repo="smartpyme",
        path="tmp/test.txt",
        content="hello",
        commit_message="test commit",
        token_provider=fake_token_provider,
        http_post=fake_http_post,
    )

    events = [json.loads(rec.message)["event"] for rec in caplog.records]
    assert "agent_min.invoke.start" in events
    assert "agent_min.invoke.finish" in events


def test_vertex_entrypoint_returns_stable_contract(monkeypatch):
    monkeypatch.setenv("SERVICE_URL", "https://code-writer-api-123.a.run.app")
    monkeypatch.setenv("INVOKER_SA", "agent@example.iam.gserviceaccount.com")

    def fake_invoke_from_payload(self, payload):
        return InvocationResult(
            status_code=200,
            ok=True,
            response_json={"status": "success", "bytes_written": 1},
        )

    monkeypatch.setattr(AgentMin, "invoke_from_payload", fake_invoke_from_payload)
    result = vertex_entrypoint(
        {
            "owner": "acme",
            "repo": "smartpyme",
            "path": "tmp/test.txt",
            "content": "hello",
            "commit_message": "test commit",
        }
    )

    assert result == {
        "status_code": 200,
        "ok": True,
        "response_json": {"status": "success", "bytes_written": 1},
    }
