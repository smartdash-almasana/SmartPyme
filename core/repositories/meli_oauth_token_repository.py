from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column, sessionmaker

from core.models.meli_oauth_token import MeliOAuthToken


Base = declarative_base()


class MeliOAuthTokenORM(Base):
    __tablename__ = "meli_oauth_tokens"

    account_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    access_token: Mapped[str] = mapped_column(String(2048), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(2048), nullable=False)
    token_type: Mapped[str] = mapped_column(String(64), nullable=False)
    scope: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_invalid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    invalid_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)


class MeliOAuthTokenRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create_schema(self) -> None:
        bind = self._session_factory.kw.get("bind")
        if bind is None:
            raise RuntimeError("SQLALCHEMY_BIND_REQUIRED")
        Base.metadata.create_all(bind)

    async def get_by_account_id(self, account_id: str) -> MeliOAuthToken | None:
        with self._session_factory() as session:
            row = session.get(MeliOAuthTokenORM, account_id)
            if row is None:
                return None
            return self._to_domain(row)

    async def upsert(self, token: MeliOAuthToken) -> None:
        with self._session_factory() as session:
            existing = session.get(MeliOAuthTokenORM, token.account_id)
            if existing is None:
                row = self._to_orm(token)
                session.add(row)
            else:
                existing.access_token = token.access_token
                existing.refresh_token = token.refresh_token
                existing.token_type = token.token_type
                existing.scope = token.scope
                existing.user_id = token.user_id
                existing.expires_at = token.expires_at
                existing.is_invalid = token.is_invalid
                existing.invalid_reason = token.invalid_reason
            session.commit()

    async def mark_invalid(self, account_id: str, reason: str) -> None:
        with self._session_factory() as session:
            existing = session.get(MeliOAuthTokenORM, account_id)
            if existing is None:
                return
            existing.is_invalid = True
            existing.invalid_reason = reason
            session.commit()

    def _to_domain(self, row: MeliOAuthTokenORM) -> MeliOAuthToken:
        return MeliOAuthToken(
            account_id=row.account_id,
            access_token=row.access_token,
            refresh_token=row.refresh_token,
            token_type=row.token_type,
            scope=row.scope,
            user_id=row.user_id,
            expires_at=self._normalize_utc_datetime(row.expires_at),
            is_invalid=row.is_invalid,
            invalid_reason=row.invalid_reason,
        )

    def _to_orm(self, token: MeliOAuthToken) -> MeliOAuthTokenORM:
        return MeliOAuthTokenORM(
            account_id=token.account_id,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            scope=token.scope,
            user_id=token.user_id,
            expires_at=self._normalize_utc_datetime(token.expires_at),
            is_invalid=token.is_invalid,
            invalid_reason=token.invalid_reason,
        )

    def _normalize_utc_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
