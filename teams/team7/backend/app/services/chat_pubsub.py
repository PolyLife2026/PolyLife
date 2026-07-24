"""Redis pub/sub helpers for chat fan-out (SCRUM-11).

Channel naming
--------------
- ``team7:chat:thread:{thread_id}`` — per-thread event stream. Every
  WebSocket connected to the thread subscribes; every send / typing /
  read publishes here.
- ``team7:chat:presence`` — global coach presence stream. Every
  WebSocket subscribes to receive ``presence.update`` events when a
  coach toggles ``is_online``.

Event envelope
--------------
Publishes are JSON strings with two top-level keys:

    { "event": "<name>", "data": { ... } }

The shape of ``data`` matches the Pydantic ``Ws*Data`` schemas in
``app.schemas.chat_ws`` and is consumed directly by the WebSocket
handler's outbound writer.
"""

from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

THREAD_CHANNEL_TEMPLATE = "team7:chat:thread:{thread_id}"
PRESENCE_CHANNEL = "team7:chat:presence"


def thread_channel(thread_id: int) -> str:
    """Return the Redis pub/sub channel for a chat thread."""
    return THREAD_CHANNEL_TEMPLATE.format(thread_id=thread_id)


async def publish_event(
    redis_client: Redis,
    *,
    channel: str,
    event: str,
    data: dict[str, Any],
) -> int:
    """Publish an event to ``channel``; returns the subscriber match count.

    See :func:`redis.asyncio.Redis.publish` for the return-value contract.
    """
    payload = json.dumps({"event": event, "data": data}, default=str)
    return await redis_client.publish(channel, payload)


async def subscribe_thread(
    redis_client: Redis,
    thread_id: int,
) -> Any:
    """Subscribe the given PubSub to a thread's channel; returns the PubSub.

    Kept as a thin wrapper so the channel-naming policy lives in one
    place and tests can substitute a recording fake.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(thread_channel(thread_id))
    return pubsub


async def subscribe_presence(redis_client: Redis) -> Any:
    """Subscribe the given PubSub to the global presence channel."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(PRESENCE_CHANNEL)
    return pubsub
