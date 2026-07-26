"""Shared async Redis client for chat pub/sub and rate-limiting.

A single ``redis.asyncio.Redis`` instance is created at application startup
(``init_redis_client``) and shared across all WebSocket handlers. Each
handler obtains its own short-lived ``PubSub`` via ``get_redis_client().pubsub()``
so that Redis connections are pooled efficiently while per-subscription
state stays isolated.

The URL is read from ``settings.url_redis`` (env var ``URL_REDIS``). In
production the Docker compose service name ``redis`` resolves on the
private ``team`` network; in tests ``conftest.py`` pins it to
``redis://localhost:6379/0`` and overrides the singleton with a
``fakeredis`` instance.
"""

from __future__ import annotations

import redis.asyncio

from app.core.config import settings

_client: redis.asyncio.Redis | None = None


def init_redis_client(client: redis.asyncio.Redis | None = None) -> redis.asyncio.Redis:
    """Create the shared Redis client (or inject a fake for tests).

    Called from the FastAPI lifespan startup phase. Passing a non-``None``
    ``client`` installs it directly — used by tests to inject
    ``fakeredis.aioredis.FakeRedis``.
    """
    global _client
    if client is None:
        _client = redis.asyncio.from_url(
            settings.url_redis,
            decode_responses=True,
        )
    else:
        _client = client
    return _client


async def close_redis_client() -> None:
    """Close the shared Redis client during application shutdown."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def get_redis_client() -> redis.asyncio.Redis:
    """Return the shared Redis client.

    Raises ``RuntimeError`` if the client was never initialised — this
    surfaces a misconfigured lifespan rather than silently returning
    ``None`` at WebSocket time.
    """
    if _client is None:
        raise RuntimeError(
            "Redis client is not initialised. "
            "Call init_redis_client() during application startup."
        )
    return _client


def reset_redis_client_for_tests() -> None:
    """Drop the cached client reference; tests re-initialise with fakes."""
    global _client
    _client = None
