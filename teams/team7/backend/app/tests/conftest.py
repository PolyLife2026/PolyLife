"""Shared pytest fixtures.

The ``client`` fixture serves the in-process ASGI app through httpx for
fast HTTP-level tests. ``db_session`` + ``db_engine`` fixtures share the
application's global engine so the WebSocket handler — which creates
its own short-lived sessions via ``AsyncSessionLocal`` — sees the same
schema and data as the per-test ``db_session`` fixture.

``fake_redis`` installs a ``fakeredis.aioredis.FakeRedis`` instance as
the shared Redis client so the WebSocket tests can exercise the pub/sub
fan-out without a running Redis container.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Awaitable, Callable
from decimal import Decimal

# Point the app at an in-memory SQLite before any of the application's
# modules import `app.core.config` / `app.core.db` (both create their
# engine at import time using ``settings.database_url``).
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("URL_REDIS", "redis://localhost:6379/0")
os.environ.setdefault("CORE_BASE_URL", "http://core:8000")
os.environ.setdefault("LOG_LEVEL", "info")

import fakeredis.aioredis
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.core.db import (
    AsyncSessionLocal,
    get_db,
    override_async_session_local,
)
from app.core.db import (
    engine as app_engine,
)
from app.core.redis import (
    close_redis_client,
    init_redis_client,
    reset_redis_client_for_tests,
)
from app.main import app
from app.models import Base
from app.models.coach_profile import CoachProfile


@pytest_asyncio.fixture
async def fake_redis() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    """Install a ``fakeredis`` client as the shared Redis client.

    ``fakeredis`` supports ``redis.asyncio`` pub/sub and ``publish``/
    ``subscribe`` semantics, which is what the WebSocket handler uses.
    """
    reset_redis_client_for_tests()
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    init_redis_client(client)
    try:
        yield client
    finally:
        await close_redis_client()
        reset_redis_client_for_tests()


@pytest_asyncio.fixture
async def db_engine() -> AsyncIterator:
    """Yield the application engine; create the schema and clean up after.

    All fixtures in this module share this engine so the WebSocket
    handler (which opens its own short-lived sessions) sees the same
    database as the per-test ``db_session`` fixture.
    """
    async with app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    @event.listens_for(app_engine.sync_engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    try:
        yield app_engine
    finally:
        async with app_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_engine) -> AsyncClient:  # noqa: ARG001
    """HTTPX async client bound to the in-process FastAPI app.

    Depends on ``db_engine`` so the schema exists before the app starts.
    Installs a per-test fake Redis and points the global
    ``AsyncSessionLocal`` at the test engine so long-lived callers
    (e.g. the WebSocket handler) see the same database.
    """
    reset_redis_client_for_tests()
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    init_redis_client(fake)
    session_factory = async_sessionmaker(
        bind=app_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    override_async_session_local(session_factory)
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as ac:
            yield ac
    finally:
        override_async_session_local(None)
        await close_redis_client()
        reset_redis_client_for_tests()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncIterator[AsyncSession]:  # type: ignore[no-untyped-def]
    """Function-scoped async session sharing the test engine."""

    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def make_coach(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[CoachProfile]]:  # type: ignore[no-untyped-def]
    """Factory that inserts a ``CoachProfile`` row for use as an FK target."""

    counter = {"n": 0}

    async def _factory(*, user_id: int | None = None, is_deleted: bool = False) -> CoachProfile:
        counter["n"] += 1
        if user_id is None:
            user_id = 1000 + counter["n"]
        profile = CoachProfile(
            user_id=user_id,
            hourly_rate=Decimal("0"),
            is_deleted=is_deleted,
        )
        db_session.add(profile)
        await db_session.flush()
        return profile

    return _factory


@pytest_asyncio.fixture
async def override_db(db_session: AsyncSession) -> AsyncIterator[AsyncSession]:
    """Install the per-test session as the FastAPI ``get_db`` dependency."""

    async def _override() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = _override
    try:
        yield db_session
    finally:
        app.dependency_overrides.pop(get_db, None)
