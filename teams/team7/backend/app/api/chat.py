"""Chat with-coach HTTP router (SCRUM-8, SCRUM-14, SCRUM-15).

Public, gateway-facing routes are ``/api/chat/...``. The Nginx gateway
removes the public ``/api/`` prefix before forwarding requests, so this
router is mounted at ``prefix="/chat"``. See ``teams/team7/gateway.conf``
and ``app/api/meta.py`` for the precedent.

This router covers thread management, coach online-status endpoints, and
thread attachment upload. Messages, WebSocket delivery, and reserve
features belong to later tickets.
"""

from __future__ import annotations

from email.message import Message

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.redis import get_redis_client
from app.core.security import CurrentUser, get_current_user
from app.schemas.chat import (
    ChatAttachmentRead,
    ChatAttachmentResponse,
    ChatMessageRead,
    ChatMessageResponse,
    ChatThreadCreateRequest,
    ChatThreadListResponse,
    ChatThreadRead,
    ChatThreadResponse,
    CoachOnlineStatusUpdateRequest,
)
from app.schemas.reserve import CoachProfileListResponse, CoachProfileRead, CoachProfileResponse
from app.services import chat as chat_service
from app.services import chat_ws as chat_ws_service
from app.services.chat_pubsub import publish_event, thread_channel

router = APIRouter(prefix="/chat", tags=["chat"])


def _extract_uploaded_file(request: Request, body: bytes) -> tuple[str, str, bytes]:
    """Parse the single-file multipart payload used by the attachment upload."""

    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("multipart/form-data"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expected multipart/form-data upload.",
        )

    content_type_message = Message()
    content_type_message["content-type"] = content_type
    boundary = content_type_message.get_param("boundary", header="content-type")
    if not boundary:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing multipart boundary.",
        )

    delimiter = f"--{boundary}".encode()
    for raw_part in body.split(delimiter):
        # Remove only the multipart framing. ``strip()`` would corrupt a
        # legitimate file whose first or final bytes are whitespace.
        part = raw_part[2:] if raw_part.startswith(b"\r\n") else raw_part
        if not part or part == b"--":
            continue
        if part.endswith(b"--"):
            part = part[:-2].rstrip(b"\r\n")

        header_block, separator, content = part.partition(b"\r\n\r\n")
        if not separator:
            continue

        headers: dict[str, str] = {}
        for line in header_block.split(b"\r\n"):
            if b":" not in line:
                continue
            name, value = line.split(b":", 1)
            headers[name.decode("utf-8").strip().lower()] = value.decode("utf-8").strip()

        disposition_message = Message()
        disposition_message["content-disposition"] = headers.get("content-disposition", "")
        if disposition_message.get_content_disposition() != "form-data":
            continue
        if disposition_message.get_param("name", header="content-disposition") != "file":
            continue

        filename = (
            disposition_message.get_param("filename", header="content-disposition")
            or "attachment.bin"
        )
        mime_type = headers.get("content-type", "application/octet-stream")
        if content.endswith(b"\r\n"):
            content = content[:-2]
        return filename, mime_type, content

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Multipart field 'file' is required.",
    )


@router.get("/threads", response_model=ChatThreadListResponse)
async def list_threads(
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> ChatThreadListResponse:
    """List active chat threads the current user participates in."""

    rows = await chat_service.list_threads_for_user(session, current_user.id)
    return ChatThreadListResponse(data=[ChatThreadRead.model_validate(row) for row in rows])


@router.post("/threads")
async def open_or_fetch_thread(
    payload: ChatThreadCreateRequest,
    response: Response,
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> ChatThreadResponse:
    """Open or return the unique active thread between the current user and a coach."""

    if payload.coach_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot create a chat thread with yourself.",
        )

    if not await chat_service.coach_profile_exists(session, payload.coach_user_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Coach not found.",
        )

    thread, created = await chat_service.get_or_create_thread(
        session,
        user_id=current_user.id,
        coach_user_id=payload.coach_user_id,
    )
    response.status_code = (
        status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )
    return ChatThreadResponse(data=ChatThreadRead.model_validate(thread))


@router.get("/coaches/online", response_model=CoachProfileListResponse)
async def list_online_coaches(
    _current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> CoachProfileListResponse:
    """List coaches currently marked as online."""

    rows = await chat_service.list_online_coaches(session)
    return CoachProfileListResponse(
        data=[CoachProfileRead.model_validate(row) for row in rows]
    )


@router.patch("/coaches/me/status", response_model=CoachProfileResponse)
async def update_my_online_status(
    payload: CoachOnlineStatusUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> CoachProfileResponse:
    """Toggle the caller's online status."""

    row = await chat_service.update_current_coach_status(
        session,
        coach_user_id=current_user.id,
        payload=payload,
    )
    return CoachProfileResponse(data=CoachProfileRead.model_validate(row))


@router.post(
    "/threads/{thread_id}/attachments",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatAttachmentResponse,
)
async def upload_thread_attachment(
    thread_id: int,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> ChatAttachmentResponse:
    """Upload a file attachment to a chat thread."""

    thread = await chat_service.get_active_thread(session, thread_id)
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat thread not found.",
        )
    if current_user.id not in (thread.user_id, thread.coach_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat thread.",
        )

    body = await request.body()
    filename, mime_type, content = _extract_uploaded_file(request, body)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    attachment = await chat_service.create_thread_attachment(
        session,
        thread=thread,
        sender_user_id=current_user.id,
        filename=filename,
        mime_type=mime_type,
        content=content,
    )
    return ChatAttachmentResponse(data=ChatAttachmentRead.model_validate(attachment))


@router.post(
    "/threads/{thread_id}/messages/{message_id}/read",
    response_model=ChatMessageResponse,
)
async def mark_message_as_read(
    thread_id: int,
    message_id: int,
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> ChatMessageResponse:
    """Mark a message as read and broadcast a ``message.read`` WebSocket event.

    The caller must be a participant in the thread. The event is
    best-effort: the REST call succeeds even if Redis is temporarily
    unavailable.
    """
    thread = await chat_service.get_active_thread(session, thread_id)
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat thread not found.",
        )
    if current_user.id not in (thread.user_id, thread.coach_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat thread.",
        )

    message = await chat_ws_service.mark_message_read(
        session,
        thread=thread,
        message_id=message_id,
        reader_user_id=current_user.id,
    )
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found in this thread.",
        )
    await session.commit()
    await session.refresh(message)

    try:
        redis_client = get_redis_client()
        await publish_event(
            redis_client,
            channel=thread_channel(thread.id),
            event="message.read",
            data={
                "message_id": message.id,
                "thread_id": thread.id,
                "reader_user_id": current_user.id,
                "read_at": (message.read_at or message.updated_at or message.created_at).isoformat(),
            },
        )
    except Exception:
        # Presence / read fan-out is non-critical.
        pass

    return ChatMessageResponse(data=ChatMessageRead.model_validate(message))
