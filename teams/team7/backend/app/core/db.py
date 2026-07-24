"""Async SQLAlchemy engine + session factory.

`get_db` is the FastAPI dependency that yields an `AsyncSession` bound
to the team's `DATABASE_URL`. Sessions are short-lived and scoped to a
single request. Long-lived callers (e.g. the WebSocket handler) use
``AsyncSessionLocal`` directly so they can scope a session per
operation.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding an `AsyncSession` per request."""
    async with AsyncSessionLocal() as session:
        yield session


def override_async_session_local(
    factory: async_sessionmaker[AsyncSession] | None,
) -> None:
    """Replace the global ``AsyncSessionLocal`` (used by long-lived callers).

    Tests install a factory bound to the per-test in-memory SQLite
    engine so the WebSocket handler sees the same data as the
    ``db_session`` fixture. Passing ``None`` restores the default.
    """
    if factory is None:
        globals()["AsyncSessionLocal"] = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
    else:
        globals()["AsyncSessionLocal"] = factory
