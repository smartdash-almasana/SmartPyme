from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MeliOAuthToken:
    account_id: str
    access_token: str
    refresh_token: str
    token_type: str
    scope: str
    user_id: int
    expires_at: datetime
    is_invalid: bool = False
    invalid_reason: str | None = None
