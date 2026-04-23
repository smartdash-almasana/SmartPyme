from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Protocol

from core.adapters.meli_oauth_client import MeliOAuthClient, MeliOAuthError, MeliTokenResponse
from core.models.meli_oauth_token import MeliOAuthToken


class MeliTokenRepository(Protocol):
    async def get_by_account_id(self, account_id: str) -> MeliOAuthToken | None: ...

    async def upsert(self, token: MeliOAuthToken) -> None: ...

    async def mark_invalid(self, account_id: str, reason: str) -> None: ...


class MeliTokenManager:
    def __init__(
        self,
        *,
        oauth_client: MeliOAuthClient,
        repository: MeliTokenRepository,
        refresh_margin_seconds: int = 120,
    ) -> None:
        self._oauth_client = oauth_client
        self._repository = repository
        self._refresh_margin = timedelta(seconds=refresh_margin_seconds)
        self._locks: dict[str, asyncio.Lock] = {}
        self._locks_guard = asyncio.Lock()

    async def get_valid_token(self, account_id: str) -> str:
        token = await self._repository.get_by_account_id(account_id)
        if token is None:
            raise RuntimeError("MELI_TOKEN_NOT_FOUND")
        if token.is_invalid:
            raise RuntimeError("MELI_TOKEN_INVALID")
        if not self._needs_refresh(token):
            return token.access_token

        lock = await self._get_account_lock(account_id)
        async with lock:
            latest = await self._repository.get_by_account_id(account_id)
            if latest is None:
                raise RuntimeError("MELI_TOKEN_NOT_FOUND")
            if latest.is_invalid:
                raise RuntimeError("MELI_TOKEN_INVALID")
            if not self._needs_refresh(latest):
                return latest.access_token

            try:
                refreshed = await self._oauth_client.refresh_token(latest.refresh_token)
            except MeliOAuthError as exc:
                if self._is_invalid_grant(exc):
                    await self._repository.mark_invalid(account_id, "invalid_grant")
                    raise RuntimeError("MELI_REFRESH_INVALID_GRANT") from exc
                raise

            updated = self._token_from_response(account_id, refreshed)
            await self._repository.upsert(updated)
            return updated.access_token

    async def save_initial_tokens(self, account_id: str, token_response: MeliTokenResponse) -> None:
        token = self._token_from_response(account_id, token_response)
        await self._repository.upsert(token)

    async def invalidate_token(self, account_id: str, reason: str) -> None:
        await self._repository.mark_invalid(account_id, reason)

    async def _get_account_lock(self, account_id: str) -> asyncio.Lock:
        async with self._locks_guard:
            lock = self._locks.get(account_id)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[account_id] = lock
            return lock

    def _needs_refresh(self, token: MeliOAuthToken) -> bool:
        now = datetime.now(timezone.utc)
        return token.expires_at <= (now + self._refresh_margin)

    def _is_invalid_grant(self, error: MeliOAuthError) -> bool:
        details = (error.details or "").lower()
        return "invalid_grant" in details

    def _token_from_response(self, account_id: str, token_response: MeliTokenResponse) -> MeliOAuthToken:
        return MeliOAuthToken(
            account_id=account_id,
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            token_type=token_response.token_type,
            scope=token_response.scope,
            user_id=token_response.user_id,
            expires_at=token_response.expires_at,
            is_invalid=False,
            invalid_reason=None,
        )
