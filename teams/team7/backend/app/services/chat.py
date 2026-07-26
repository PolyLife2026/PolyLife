"""Chat service layer (SCRUM-8, SCRUM-14, SCRUM-15).

Pure database functions for the chat with-coach service. The HTTP layer
in ``app.api.chat`` depends on these so router tests can stay focused on
request/response shape and authorisation.

Idempotency / uniqueness contract for ``get_or_create_thread``:

- There is at most one *active* thread per ``(user_id, coach_user_id)``
  pair; the database enforces this with
  ``uq_chat_thread_user_coach`` on ``chat_thread``.
- If an active row exists, it is returned (``created=False``).
- If a *soft-deleted* row already exists for the same pair, the call
  returns ``HTTP 409 Conflict`` and refuses to silently resurrect it.
  Restoring a soft-deleted thread is a separate audit-sensitive
  operation; it is out of scope for SCRUM-8.
- If the pair is genuinely new, a fresh row is inserted. If two parallel
  inserts race, the loser's ``IntegrityError`` is rolled back and the
  surviving row is returned (``created=False``).
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import _utcnow
from app.models.chat_message import ChatMessage
from app.models.chat_thread import ChatThread
from app.models.coach_profile import CoachProfile
from app.models.message_attachment import MessageAttachment
from app.schemas.chat import CoachOnlineStatusUpdateRequest
from app.services import reserve as reserve_service


async def coach_profile_exists(session: AsyncSession, coach_user_id: int) -> bool:
    """Return True iff an active ``coach_profile`` row exists for the given id."""

    stmt = select(CoachProfile.user_id).where(
        CoachProfile.user_id == coach_user_id,
        CoachProfile.is_deleted.is_(False),
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def list_online_coaches(session: AsyncSession) -> list[dict]:
    """Return active coach profiles currently marked online."""

    rows = await reserve_service.list_coach_profiles(session)
    return [row for row in rows if row["is_online"]]


async def update_current_coach_status(
    session: AsyncSession,
    *,
    coach_user_id: int,
    payload: CoachOnlineStatusUpdateRequest,
) -> dict:
    """Toggle the caller's ``is_online`` flag and return the public profile."""

    stmt = select(CoachProfile).where(
        CoachProfile.user_id == coach_user_id,
        CoachProfile.is_deleted.is_(False),
    )
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No coach profile found for the current user.",
        )

    previous = profile.is_online
    profile.is_online = payload.is_online
    profile.updated_at = _utcnow()
    await session.commit()

    row = await reserve_service.get_coach_profile(session, coach_user_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load coach profile after status update.",
        )

    # Best-effort presence fan-out. The endpoint stays successful even if
    # Redis is temporarily unavailable — the WebSocket layer will
    # reconcile on the next status toggle.
    if previous != payload.is_online:
        try:
            from app.core.redis import get_redis_client
            from app.services.chat_pubsub import PRESENCE_CHANNEL, publish_event

            redis_client = get_redis_client()
            await publish_event(
                redis_client,
                channel=PRESENCE_CHANNEL,
                event="presence.update",
                data={"coach_user_id": coach_user_id, "is_online": payload.is_online},
            )
        except Exception:
            # Presence is non-critical; don't fail the REST call.
            pass
    return row


async def list_threads_for_user(
    session: AsyncSession, user_id: int
) -> Sequence[ChatThread]:
    """Return the active threads the user participates in, newest first.

    A user "participates" if they appear as either the regular user
    (``user_id``) or the coach (``coach_user_id``). Soft-deleted rows are
    excluded. Ordering is ``last_message_at DESC NULLS LAST`` with ``id DESC``
    as a deterministic tie-breaker.
    """

    stmt = (
        select(ChatThread)
        .where(
            ChatThread.is_deleted.is_(False),
            or_(
                ChatThread.user_id == user_id,
                ChatThread.coach_user_id == user_id,
            ),
        )
        .order_by(ChatThread.last_message_at.desc().nulls_last(), ChatThread.id.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_or_create_thread(
    session: AsyncSession, *, user_id: int, coach_user_id: int
) -> tuple[ChatThread, bool]:
    """Return the unique active thread for ``(user_id, coach_user_id)``.

    The boolean is ``True`` iff a new row was inserted by this call.

    Raises ``HTTPException(409)`` if an inactive (soft-deleted) thread
    already exists for the same pair, or if a parallel insert lost the
    race against an unrelated unhandled constraint violation.
    """

    # Fast path: active row already exists.
    existing = await _fetch_active_thread(session, user_id, coach_user_id)
    if existing is not None:
        return existing, False

    # Reject rather than resurrect a soft-deleted row.
    soft_deleted = await _fetch_soft_deleted_thread(session, user_id, coach_user_id)
    if soft_deleted is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A previously closed thread for this pair exists; reopen it explicitly.",
        )

    # Insert and handle the unique-constraint race.
    thread = ChatThread(user_id=user_id, coach_user_id=coach_user_id)
    session.add(thread)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raced = await _fetch_active_thread(session, user_id, coach_user_id)
        if raced is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Unexpected constraint violation while creating thread.",
            ) from None
        return raced, False
    await session.refresh(thread)
    return thread, True


async def _fetch_active_thread(
    session: AsyncSession, user_id: int, coach_user_id: int
) -> ChatThread | None:
    stmt = select(ChatThread).where(
        ChatThread.user_id == user_id,
        ChatThread.coach_user_id == coach_user_id,
        ChatThread.is_deleted.is_(False),
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def _fetch_soft_deleted_thread(
    session: AsyncSession, user_id: int, coach_user_id: int
) -> ChatThread | None:
    stmt = select(ChatThread).where(
        ChatThread.user_id == user_id,
        ChatThread.coach_user_id == coach_user_id,
        ChatThread.is_deleted.is_(True),
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_active_thread(session: AsyncSession, thread_id: int) -> ChatThread | None:
    """Return the active thread by id if it exists."""

    stmt = select(ChatThread).where(
        ChatThread.id == thread_id,
        ChatThread.is_deleted.is_(False),
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_thread_messages(
    session: AsyncSession, thread_id: int
) -> Sequence[ChatMessage]:
    """Return active messages in chronological order for one thread."""

    stmt = (
        select(ChatMessage)
        .where(
            ChatMessage.thread_id == thread_id,
            ChatMessage.is_deleted.is_(False),
        )
        .order_by(ChatMessage.sent_at.asc(), ChatMessage.id.asc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_thread_attachment(
    session: AsyncSession,
    *,
    thread: ChatThread,
    sender_user_id: int,
    filename: str,
    mime_type: str,
    content: bytes,
) -> MessageAttachment:
    """Persist an uploaded file via a placeholder message + attachment row."""

    attachment_dir = Path(gettempdir()) / "team7_chat_attachments"
    attachment_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(filename).name or "attachment.bin"
    stored_name = f"{uuid4().hex}_{safe_name}"
    stored_path = attachment_dir / stored_name
    stored_path.write_bytes(content)

    message = ChatMessage(
        thread_id=thread.id,
        sender_user_id=sender_user_id,
        body="",
    )
    session.add(message)
    await session.flush()

    attachment = MessageAttachment(
        message_id=message.id,
        file_url=f"file://{stored_path}",
        mime_type=mime_type or "application/octet-stream",
        size_bytes=len(content),
    )
    session.add(attachment)
    thread.last_message_at = _utcnow()
    thread.updated_at = _utcnow()

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        if stored_path.exists():
            stored_path.unlink()
        raise

    await session.refresh(attachment)
    return attachment
