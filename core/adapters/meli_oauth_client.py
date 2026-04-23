from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx


@dataclass(frozen=True)
class MeliTokenResponse:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    scope: str
    user_id: int
    expires_at: datetime


class MeliOAuthError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, details: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class MeliOAuthClient:
    def __init__(
        self,
        *,
        app_id: str,
        client_secret: str,
        redirect_uri: str,
        base_url: str = "https://api.mercadolibre.com",
        timeout: float = 15.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._app_id = app_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._transport = transport

    async def exchange_code_for_tokens(self, code: str) -> MeliTokenResponse:
        payload = {
            "grant_type": "authorization_code",
            "client_id": self._app_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": self._redirect_uri,
        }
        data = await self._post_token(payload)
        return self._build_token_response(data)

    async def refresh_token(self, refresh_token: str) -> MeliTokenResponse:
        payload = {
            "grant_type": "refresh_token",
            "client_id": self._app_id,
            "client_secret": self._client_secret,
            "refresh_token": refresh_token,
        }
        data = await self._post_token(payload)
        return self._build_token_response(data)

    async def _post_token(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            transport=self._transport,
        ) as client:
            response = await client.post("/oauth/token", data=payload)

        if response.status_code >= 400:
            raise MeliOAuthError(
                "MELI_OAUTH_HTTP_ERROR",
                status_code=response.status_code,
                details=response.text,
            )

        try:
            parsed = response.json()
        except ValueError as exc:
            raise MeliOAuthError("MELI_OAUTH_INVALID_JSON", status_code=response.status_code) from exc

        if not isinstance(parsed, dict):
            raise MeliOAuthError("MELI_OAUTH_INVALID_PAYLOAD", status_code=response.status_code)
        return parsed

    def _build_token_response(self, payload: dict[str, Any]) -> MeliTokenResponse:
        expires_in = int(payload["expires_in"])
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return MeliTokenResponse(
            access_token=str(payload["access_token"]),
            refresh_token=str(payload["refresh_token"]),
            token_type=str(payload["token_type"]),
            expires_in=expires_in,
            scope=str(payload.get("scope", "")),
            user_id=int(payload["user_id"]),
            expires_at=expires_at,
        )
