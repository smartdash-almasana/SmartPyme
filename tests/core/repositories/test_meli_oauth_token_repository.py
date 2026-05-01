import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from core.models.meli_oauth_token import MeliOAuthToken


def _build_repo():
    sqlalchemy = pytest.importorskip("sqlalchemy")
    create_engine = sqlalchemy.create_engine
    orm_module = __import__("sqlalchemy.orm", fromlist=["Session", "sessionmaker"])
    pool_module = __import__("sqlalchemy.pool", fromlist=["StaticPool"])
    Session = orm_module.Session
    sessionmaker = orm_module.sessionmaker
    StaticPool = pool_module.StaticPool
    repo_module = __import__(
        "core.repositories.meli_oauth_token_repository",
        fromlist=["MeliOAuthTokenRepository", "MeliOAuthTokenORM"],
    )

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    repo = repo_module.MeliOAuthTokenRepository(factory)
    repo.create_schema()
    return repo, repo_module.MeliOAuthTokenORM


def _token(account_id: str, suffix: str, expires_in_seconds: int) -> MeliOAuthToken:
    return MeliOAuthToken(
        account_id=account_id,
        access_token=f"access-{suffix}",
        refresh_token=f"refresh-{suffix}",
        token_type="bearer",
        scope="offline_access",
        user_id=101,
        expires_at=datetime.now(UTC) + timedelta(seconds=expires_in_seconds),
    )


def test_save_initial_token() -> None:
    repo, _ = _build_repo()
    token = _token("acc-1", "v1", 3600)

    asyncio.run(repo.upsert(token))
    loaded = asyncio.run(repo.get_by_account_id("acc-1"))

    assert loaded is not None
    assert loaded.account_id == "acc-1"
    assert loaded.access_token == "access-v1"
    assert loaded.refresh_token == "refresh-v1"


def test_get_by_account_id_returns_expected_token() -> None:
    repo, _ = _build_repo()
    token = _token("acc-2", "v1", 1800)
    asyncio.run(repo.upsert(token))

    loaded = asyncio.run(repo.get_by_account_id("acc-2"))

    assert loaded is not None
    assert loaded.token_type == "bearer"
    assert loaded.scope == "offline_access"
    assert loaded.user_id == 101


def test_upsert_updates_access_refresh_and_expires_at() -> None:
    repo, _ = _build_repo()
    first = _token("acc-3", "v1", 60)
    second = _token("acc-3", "v2", 7200)

    asyncio.run(repo.upsert(first))
    asyncio.run(repo.upsert(second))
    loaded = asyncio.run(repo.get_by_account_id("acc-3"))

    assert loaded is not None
    assert loaded.access_token == "access-v2"
    assert loaded.refresh_token == "refresh-v2"
    assert loaded.expires_at.tzinfo == UTC
    assert loaded.expires_at == second.expires_at


def test_mark_invalid_sets_flag_and_reason() -> None:
    repo, _ = _build_repo()
    token = _token("acc-4", "v1", 3600)
    asyncio.run(repo.upsert(token))

    asyncio.run(repo.mark_invalid("acc-4", "invalid_grant"))
    loaded = asyncio.run(repo.get_by_account_id("acc-4"))

    assert loaded is not None
    assert loaded.is_invalid is True
    assert loaded.invalid_reason == "invalid_grant"


def test_upsert_does_not_duplicate_account_id() -> None:
    repo, orm_cls = _build_repo()
    first = _token("acc-5", "v1", 3600)
    second = _token("acc-5", "v2", 3600)
    asyncio.run(repo.upsert(first))
    asyncio.run(repo.upsert(second))

    sqlalchemy = pytest.importorskip("sqlalchemy")
    select = sqlalchemy.select
    func = sqlalchemy.func
    with repo._session_factory() as session:
        rows = int(session.scalar(select(func.count()).select_from(orm_cls)) or 0)

    assert rows == 1
