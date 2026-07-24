"""WebSocket chat business logic (SCRUM-11).

This module hosts the persistence-side helpers used by the
``/chat/ws`` WebSocket handler. It deliberately does not touch any
``WebSocket`` or Redis API directly — those concerns live in
``app.api.chat_ws`` and ``app.services.chat_pubsub`` so this layer
stays testable with a plain ``AsyncSession``.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import _utcnow
from app.models.chat_message import ChatMessage
from app.models.chat_thread import ChatThread
from app.services.chat import get_active_thread


async def persist_chat_message(
    session: AsyncSession,
    *,
    thread: ChatThread,
    sender_user_id: int,
    body: str,
) -> ChatMessage:
    """Insert a new ``chat_message`` row and bump the thread's ``last_message_at``.

    The caller is responsible for the transaction lifecycle (commit /
    rollback) and for the prior participant check on ``thread``.
    """
    message = ChatMessage(
        thread_id=thread.id,
        sender_user_id=sender_user_id,
        body=body,
    )
    session.add(message)
    await session.flush()
    thread.last_message_at = message.sent_at
    thread.updated_at = _utcnow()
    await session.flush()
    return message


async def mark_message_read(
    session: AsyncSession,
    *,
    thread: ChatThread,
    message_id: int,
    reader_user_id: int,
) -> ChatMessage | None:
    """Set ``read_at`` on ``message_id`` if it belongs to ``thread``.

    Returns the updated ``ChatMessage``, or ``None`` if the message does
    not exist in this thread (already-read messages are returned as-is
    with their existing ``read_at``). The caller is responsible for the
    participant check on ``thread`` and for committing the session.
    """
    stmt = select(ChatMessage).where(
        ChatMessage.id == message_id,
        ChatMessage.thread_id == thread.id,
        ChatMessage.is_deleted.is_(False),
    )
    result = await session.execute(stmt)
    message = result.scalar_one_or_none()
    if message is None:
        return None
    if message.read_at is None:
        message.read_at = _utcnow()
        await session.flush()
    # Touch the unused argument so static analysers see the intent.
    _ = reader_user_id
    return message


async def load_thread_for_participant(
    session: AsyncSession,
    *,
    thread_id: int,
    user_id: int,
) -> ChatThread | None:
    """Return the thread if it exists, is active, and ``user_id`` participates.

    A user "participates" if they appear as either the regular user
    (``user_id``) or the coach (``coach_user_id``). This is the same
    rule the REST router uses.
    """
    thread = await get_active_thread(session, thread_id)
    if thread is None:
        return None
    if user_id not in (thread.user_id, thread.coach_user_id):
        return None
    return thread
