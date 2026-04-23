import asyncio
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from core.adapters.meli_oauth_client import MeliOAuthError, MeliTokenResponse
from core.models.meli_oauth_token import MeliOAuthToken
from core.services.meli_token_manager import MeliTokenManager


class _FakeRepository:
    def __init__(self) -> None:
        self._store: dict[str, MeliOAuthToken] = {}

    async def get_by_account_id(self, account_id: str) -> MeliOAuthToken | None:
        return self._store.get(account_id)

    async def upsert(self, token: MeliOAuthToken) -> None:
        self._store[token.account_id] = token

    async def mark_invalid(self, account_id: str, reason: str) -> None:
        current = self._store.get(account_id)
        if current is None:
            return
        self._store[account_id] = replace(current, is_invalid=True, invalid_reason=reason)


class _FakeOAuthClient:
    def __init__(self, response: MeliTokenResponse | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.calls = 0

    async def refresh_token(self, refresh_token: str) -> MeliTokenResponse:
        _ = refresh_token
        self.calls += 1
        if self._error is not None:
            raise self._error
        if self._response is None:
            raise RuntimeError("missing fake response")
        await asyncio.sleep(0.01)
        return self._response


def _token_response(access: str, refresh: str, expires_in_seconds: int) -> MeliTokenResponse:
    return MeliTokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=expires_in_seconds,
        scope="offline_access",
        user_id=99,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds),
    )


def test_save_initial_and_get_valid_token_without_refresh() -> None:
    repo = _FakeRepository()
    oauth = _FakeOAuthClient(response=_token_response("new-access", "new-refresh", 3600))
    manager = MeliTokenManager(oauth_client=oauth, repository=repo)

    initial = _token_response("access-1", "refresh-1", 3600)
    asyncio.run(manager.save_initial_tokens("acc-1", initial))

    token = asyncio.run(manager.get_valid_token("acc-1"))

    assert token == "access-1"
    assert oauth.calls == 0


def test_get_valid_token_refreshes_when_expiring_in_less_than_two_minutes() -> None:
    repo = _FakeRepository()
    expiring = MeliOAuthToken(
        account_id="acc-2",
        access_token="old-access",
        refresh_token="old-refresh",
        token_type="bearer",
        scope="offline_access",
        user_id=5,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
    )
    asyncio.run(repo.upsert(expiring))

    refreshed = _token_response("new-access", "new-refresh", 3600)
    oauth = _FakeOAuthClient(response=refreshed)
    manager = MeliTokenManager(oauth_client=oauth, repository=repo)

    token = asyncio.run(manager.get_valid_token("acc-2"))

    assert token == "new-access"
    assert oauth.calls == 1
    stored = asyncio.run(repo.get_by_account_id("acc-2"))
    assert stored is not None
    assert stored.access_token == "new-access"
    assert stored.refresh_token == "new-refresh"
    assert stored.is_invalid is False


def test_get_valid_token_marks_invalid_on_invalid_grant() -> None:
    repo = _FakeRepository()
    expiring = MeliOAuthToken(
        account_id="acc-3",
        access_token="old-access",
        refresh_token="old-refresh",
        token_type="bearer",
        scope="offline_access",
        user_id=5,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    asyncio.run(repo.upsert(expiring))

    oauth = _FakeOAuthClient(
        error=MeliOAuthError(
            "MELI_OAUTH_HTTP_ERROR",
            status_code=400,
            details='{"error":"invalid_grant"}',
        )
    )
    manager = MeliTokenManager(oauth_client=oauth, repository=repo)

    try:
        asyncio.run(manager.get_valid_token("acc-3"))
    except RuntimeError as exc:
        assert str(exc) == "MELI_REFRESH_INVALID_GRANT"
    else:
        raise AssertionError("Expected RuntimeError")

    stored = asyncio.run(repo.get_by_account_id("acc-3"))
    assert stored is not None
    assert stored.is_invalid is True
    assert stored.invalid_reason == "invalid_grant"


def test_single_flight_refresh_avoids_duplicate_concurrent_calls() -> None:
    repo = _FakeRepository()
    expiring = MeliOAuthToken(
        account_id="acc-4",
        access_token="old-access",
        refresh_token="old-refresh",
        token_type="bearer",
        scope="offline_access",
        user_id=5,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=10),
    )
    asyncio.run(repo.upsert(expiring))

    oauth = _FakeOAuthClient(response=_token_response("singleflight-access", "singleflight-refresh", 3600))
    manager = MeliTokenManager(oauth_client=oauth, repository=repo)

    async def _run_two_calls() -> tuple[str, str]:
        first, second = await asyncio.gather(
            manager.get_valid_token("acc-4"),
            manager.get_valid_token("acc-4"),
        )
        return first, second

    first_token, second_token = asyncio.run(_run_two_calls())

    assert first_token == "singleflight-access"
    assert second_token == "singleflight-access"
    assert oauth.calls == 1
