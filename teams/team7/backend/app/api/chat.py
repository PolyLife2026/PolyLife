"""Chat with-coach HTTP router (SCRUM-8, SCRUM-14).

Public, gateway-facing routes are ``/api/chat/...``; the Nginx layer
prefixes ``/api/`` via ``proxy_pass`` without a URI rewrite, so the
FastAPI router is mounted at ``prefix="/chat"`` to match the existing
``/meta`` convention. See ``teams/team7/gateway.conf`` and
``app/api/meta.py`` for the precedent.

This router covers thread management and coach online-status endpoints.
Messages, WebSocket delivery, attachments, and reserve features belong to
later tickets.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.schemas.chat import (
    ChatThreadCreateRequest,
    ChatThreadListResponse,
    ChatThreadRead,
    ChatThreadResponse,
    CoachOnlineStatusUpdateRequest,
)
from app.schemas.reserve import CoachProfileListResponse, CoachProfileRead, CoachProfileResponse
from app.services import chat as chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


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
