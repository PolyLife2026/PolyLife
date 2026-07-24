"""Chat WebSocket router (SCRUM-11).

Exposes ``WS /chat/ws?thread_id={id}`` behind the same forwarded-identity
auth flow as the REST routers. The handler is intentionally split into
small coroutines:

- ``chat_ws_endpoint`` — the FastAPI entrypoint. Validates auth, the
  ``thread_id`` query parameter, and the caller's participation in the
  thread before ``accept()``.
- ``_redis_listener`` — long-lived task that pulls events from the
  thread's Redis channel and forwards them to the WebSocket.
- ``_receive_loop`` — long-lived task that consumes client frames and
  dispatches them to the appropriate persistence / publish helper.

Both tasks are cancelled on disconnect; the Redis PubSub is always
closed in a ``finally`` block.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.core.redis import get_redis_client
from app.core.ws_security import get_current_user_for_ws
from app.schemas.chat_ws import WsReadData, WsTypingData
from app.services.chat_pubsub import (
    PRESENCE_CHANNEL,
    publish_event,
    subscribe_presence,
    subscribe_thread,
    thread_channel,
)
from app.services.chat_ws import (
    load_thread_for_participant,
    mark_message_read,
    persist_chat_message,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


async def _open_session() -> AsyncSession:
    """Open a short-lived ``AsyncSession`` for a single WS operation.

    The per-request ``get_db`` dependency is tied to the HTTP request
    lifecycle; a long-lived WebSocket must manage its own sessions.
    Tests swap the global ``AsyncSessionLocal`` (see
    ``app.core.db.override_async_session_local``) so the WS handler
    sees the same engine as the per-test fixtures.
    """
    return AsyncSessionLocal()


async def _send_json(websocket: WebSocket, payload: dict[str, Any]) -> None:
    """Serialise and send a single server-to-client frame."""
    await websocket.send_text(json.dumps(payload, default=str))


def _parse_client_frame(raw: str) -> dict[str, Any] | None:
    """Parse and lightly validate a client frame.

    Returns ``None`` for malformed JSON or unknown shapes. Callers should
    send a typed ``error`` frame back when this returns ``None``.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


@router.websocket("/chat/ws")
async def chat_ws_endpoint(
    websocket: WebSocket,
    thread_id: int = Query(gt=0, description="Chat thread id"),
) -> None:
    """Authenticated WebSocket endpoint for a chat thread.

    Auth is enforced by reading the ``X-User-*`` headers that the team
    gateway copies onto the Upgrade request. Thread access is enforced
    by checking participation in the thread before accepting.
    """
    current_user = get_current_user_for_ws(websocket)

    session = await _open_session()
    try:
        thread = await load_thread_for_participant(
            session, thread_id=thread_id, user_id=current_user.id
        )
        if thread is None:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Thread not found or access denied.",
            )
            return
        await session.close()
    except Exception:
        await session.close()
        logger.exception("WS auth check failed for thread_id=%s", thread_id)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    await websocket.accept()
    redis_client = get_redis_client()

    thread_sub = await subscribe_thread(redis_client, thread_id)
    presence_sub = await subscribe_presence(redis_client)
    sender_task: asyncio.Task[None] | None = None
    listener_task: asyncio.Task[None] | None = None
    stop = asyncio.Event()
    try:
        sender_task = asyncio.create_task(
            _receive_loop(
                websocket=websocket,
                thread_id=thread_id,
                current_user=current_user,
                stop=stop,
            ),
            name=f"chat-ws-recv-{thread_id}-{current_user.id}",
        )
        listener_task = asyncio.create_task(
            _redis_listener(
                websocket=websocket,
                subs=(thread_sub, presence_sub),
                thread_id=thread_id,
                stop=stop,
            ),
            name=f"chat-ws-pub-{thread_id}-{current_user.id}",
        )
        done, pending = await asyncio.wait(
            {sender_task, listener_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        stop.set()
        for task in pending:
            task.cancel()
        for task in done:
            exc = task.exception()
            if exc is not None and not isinstance(exc, WebSocketDisconnect):
                logger.warning("WS task ended with error: %r", exc)
    except WebSocketDisconnect:
        pass
    finally:
        stop.set()
        for task in (sender_task, listener_task):
            if task is not None and not task.done():
                task.cancel()
        try:
            await thread_sub.aclose()
        except Exception:
            logger.debug("thread_sub.aclose failed", exc_info=True)
        try:
            await presence_sub.aclose()
        except Exception:
            logger.debug("presence_sub.aclose failed", exc_info=True)
        with contextlib.suppress(Exception):
            await websocket.close()


async def _receive_loop(
    *,
    websocket: WebSocket,
    thread_id: int,
    current_user,
    stop: asyncio.Event,
) -> None:
    """Read client frames and persist / publish the corresponding events."""
    redis_client = get_redis_client()
    while not stop.is_set():
        raw = await websocket.receive_text()
        frame = _parse_client_frame(raw)
        if frame is None:
            await _send_json(
                websocket,
                {
                    "event": "error",
                    "data": {
                        "code": "BAD_FRAME",
                        "message": "Malformed JSON frame.",
                    },
                },
            )
            continue
        op = frame.get("op")
        if op == "send":
            await _handle_send(
                websocket=websocket,
                redis_client=redis_client,
                thread_id=thread_id,
                sender_user_id=current_user.id,
                body=frame.get("body"),
            )
        elif op == "typing":
            await _handle_typing(
                redis_client=redis_client,
                thread_id=thread_id,
                user_id=current_user.id,
                is_typing=frame.get("is_typing"),
            )
        elif op == "read":
            await _handle_read(
                websocket=websocket,
                thread_id=thread_id,
                reader_user_id=current_user.id,
                message_id=frame.get("message_id"),
            )
        else:
            await _send_json(
                websocket,
                {
                    "event": "error",
                    "data": {
                        "code": "UNKNOWN_OP",
                        "message": f"Unknown op: {op!r}",
                    },
                },
            )


async def _handle_send(
    *,
    websocket: WebSocket,
    redis_client,
    thread_id: int,
    sender_user_id: int,
    body: Any,
) -> None:
    """Persist a text message and publish a ``message.created`` event."""
    if not isinstance(body, str) or not body.strip():
        await _send_json(
            websocket,
            {
                "event": "error",
                "data": {
                    "code": "VALIDATION",
                    "message": "body must be a non-empty string.",
                },
            },
        )
        return

    session = await _open_session()
    try:
        thread = await load_thread_for_participant(
            session, thread_id=thread_id, user_id=sender_user_id
        )
        if thread is None:
            await _send_json(
                websocket,
                {
                    "event": "error",
                    "data": {
                        "code": "FORBIDDEN",
                        "message": "You are not a participant in this thread.",
                    },
                },
            )
            return
        message = await persist_chat_message(
            session, thread=thread, sender_user_id=sender_user_id, body=body
        )
        await session.commit()
        await session.refresh(message)
        payload = {
            "id": message.id,
            "thread_id": message.thread_id,
            "sender_user_id": message.sender_user_id,
            "body": message.body,
            "sent_at": message.sent_at.isoformat(),
        }
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

    await publish_event(
        redis_client,
        channel=thread_channel(thread_id),
        event="message.created",
        data=payload,
    )


async def _handle_typing(
    *,
    redis_client,
    thread_id: int,
    user_id: int,
    is_typing: Any,
) -> None:
    """Publish ``typing.start`` / ``typing.stop`` events."""
    if not isinstance(is_typing, bool):
        return
    event = "typing.start" if is_typing else "typing.stop"
    payload = WsTypingData(
        thread_id=thread_id,
        user_id=user_id,
        is_typing=is_typing,
    ).model_dump(mode="json")
    await publish_event(
        redis_client,
        channel=thread_channel(thread_id),
        event=event,
        data=payload,
    )


async def _handle_read(
    *,
    websocket: WebSocket,
    thread_id: int,
    reader_user_id: int,
    message_id: Any,
) -> None:
    """Mark a message as read and publish a ``message.read`` event."""
    if not isinstance(message_id, int) or message_id <= 0:
        await _send_json(
            websocket,
            {
                "event": "error",
                "data": {
                    "code": "VALIDATION",
                    "message": "message_id must be a positive integer.",
                },
            },
        )
        return

    redis_client = get_redis_client()
    session = await _open_session()
    try:
        thread = await load_thread_for_participant(
            session, thread_id=thread_id, user_id=reader_user_id
        )
        if thread is None:
            await _send_json(
                websocket,
                {
                    "event": "error",
                    "data": {"code": "FORBIDDEN", "message": "Thread denied."},
                },
            )
            return
        message = await mark_message_read(
            session,
            thread=thread,
            message_id=message_id,
            reader_user_id=reader_user_id,
        )
        if message is None:
            await _send_json(
                websocket,
                {
                    "event": "error",
                    "data": {"code": "NOT_FOUND", "message": "Message not found."},
                },
            )
            return
        await session.commit()
        read_at = message.read_at
        if read_at is None:
            read_at = datetime.utcnow()
        payload = WsReadData(
            message_id=message.id,
            thread_id=thread.id,
            reader_user_id=reader_user_id,
            read_at=read_at,
        ).model_dump(mode="json")
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

    await publish_event(
        redis_client,
        channel=thread_channel(thread_id),
        event="message.read",
        data=payload,
    )


async def _redis_listener(
    *,
    websocket: WebSocket,
    subs: tuple,
    thread_id: int,
    stop: asyncio.Event,
) -> None:
    """Forward ``team7:chat:*`` events to the local WebSocket.

    We iterate the per-thread sub first and fall back to the presence
    sub so a single ``get_message(timeout=...)`` cycle drains whichever
    channel has data. ``decode_responses=True`` on the shared client
    (see ``app.core.redis``) keeps the payloads as strings.
    """
    del thread_id  # unused — documented for future per-thread filtering
    while not stop.is_set():
        delivered = False
        for sub in subs:
            try:
                msg = await sub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            except (RedisConnectionError, RedisTimeoutError, RedisError):
                logger.warning("Redis listener error; backing off", exc_info=True)
                await asyncio.sleep(1.0)
                msg = None
            if msg is None:
                continue
            delivered = True
            data = msg.get("data")
            channel = msg.get("channel")
            if not isinstance(data, str):
                continue
            if channel == PRESENCE_CHANNEL and data.startswith("{"):
                # Presence is a global stream — forward verbatim.
                await websocket.send_text(data)
            elif data.startswith("{"):
                await websocket.send_text(data)
        if not delivered:
            await asyncio.sleep(0.01)
