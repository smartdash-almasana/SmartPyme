import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from core.adapters.meli_oauth_client import MeliOAuthClient, MeliOAuthError, MeliTokenResponse


def _token_payload(expires_in: int = 3600) -> dict[str, object]:
    return {
        "access_token": "acc-token",
        "refresh_token": "ref-token",
        "token_type": "bearer",
        "expires_in": expires_in,
        "scope": "offline_access read write",
        "user_id": 123456,
    }


def test_exchange_code_for_tokens_success_and_body() -> None:
    captured: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["body"] = request.content.decode("utf-8")
        return httpx.Response(status_code=200, json=_token_payload(1200))

    client = MeliOAuthClient(
        app_id="app-1",
        client_secret="secret-1",
        redirect_uri="https://app.test/callback",
        base_url="https://api.mercadolibre.com",
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(client.exchange_code_for_tokens("auth-code-123"))

    assert isinstance(result, MeliTokenResponse)
    assert result.access_token == "acc-token"
    assert result.refresh_token == "ref-token"
    assert result.token_type == "bearer"
    assert result.expires_in == 1200
    assert result.scope == "offline_access read write"
    assert result.user_id == 123456
    assert captured["method"] == "POST"
    assert captured["path"] == "/oauth/token"
    assert "grant_type=authorization_code" in captured["body"]
    assert "code=auth-code-123" in captured["body"]
    assert "client_id=app-1" in captured["body"]
    assert "client_secret=secret-1" in captured["body"]
    assert "redirect_uri=https%3A%2F%2Fapp.test%2Fcallback" in captured["body"]


def test_refresh_token_success_and_body() -> None:
    captured: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content.decode("utf-8")
        return httpx.Response(status_code=200, json=_token_payload())

    client = MeliOAuthClient(
        app_id="app-2",
        client_secret="secret-2",
        redirect_uri="https://app.test/callback",
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(client.refresh_token("refresh-xyz"))

    assert result.access_token == "acc-token"
    assert "grant_type=refresh_token" in captured["body"]
    assert "refresh_token=refresh-xyz" in captured["body"]
    assert "client_id=app-2" in captured["body"]
    assert "client_secret=secret-2" in captured["body"]


def test_expires_at_is_calculated_from_expires_in() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json=_token_payload(90))

    now_before = datetime.now(timezone.utc)
    client = MeliOAuthClient(
        app_id="app-3",
        client_secret="secret-3",
        redirect_uri="https://app.test/callback",
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(client.exchange_code_for_tokens("code-90"))
    now_after = datetime.now(timezone.utc)

    assert result.expires_at.tzinfo is timezone.utc
    lower_bound = now_before.timestamp() + 90
    upper_bound = now_after.timestamp() + 90
    assert lower_bound <= result.expires_at.timestamp() <= upper_bound


def test_http_error_is_raised_with_usable_data() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=401, text='{"message":"invalid_client"}')

    client = MeliOAuthClient(
        app_id="bad-app",
        client_secret="bad-secret",
        redirect_uri="https://app.test/callback",
        transport=httpx.MockTransport(handler),
    )

    try:
        asyncio.run(client.exchange_code_for_tokens("bad-code"))
    except MeliOAuthError as err:
        exc = err
    else:
        raise AssertionError("Expected MeliOAuthError")

    assert str(exc) == "MELI_OAUTH_HTTP_ERROR"
    assert exc.status_code == 401
    assert "invalid_client" in (exc.details or "")
