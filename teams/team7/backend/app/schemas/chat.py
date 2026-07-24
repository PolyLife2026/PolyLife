"""Schemas for the chat with-coach service (SCRUM-8).

These Pydantic models define the public request/response shape for
``/api/chat/threads``. They are intentionally separate from the SQLAlchemy
ORM models so the wire contract can evolve independently of the schema.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatThreadRead(BaseModel):
    """Public shape of a single chat thread."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    coach_user_id: int
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime | None


class ChatThreadCreateRequest(BaseModel):
    """POST body for opening (or returning) a thread with a coach."""

    coach_user_id: int = Field(gt=0, description="``X-User-Id`` of the coach.")


class ChatThreadListResponse(BaseModel):
    """Envelope for ``GET /api/chat/threads``."""

    data: list[ChatThreadRead]


class ChatThreadResponse(BaseModel):
    """Envelope for ``POST /api/chat/threads``."""

    data: ChatThreadRead


class CoachOnlineStatusUpdateRequest(BaseModel):
    """PATCH body for toggling a coach's online status."""

    is_online: bool


class ChatAttachmentRead(BaseModel):
    """Public shape of a chat attachment record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: int
    file_url: str
    mime_type: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime | None


class ChatAttachmentResponse(BaseModel):
    """Envelope for ``POST /api/chat/threads/{thread_id}/attachments``."""

    data: ChatAttachmentRead


class ChatMessageRead(BaseModel):
    """Public shape of a single chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    thread_id: int
    sender_user_id: int
    body: str
    sent_at: datetime
    read_at: datetime | None
    created_at: datetime
    updated_at: datetime | None


class ChatMessageCreateRequest(BaseModel):
    """POST body for sending a text message to a thread."""

    body: str = Field(min_length=1, max_length=8000)

    @field_validator("body")
    @classmethod
    def body_must_contain_text(cls, value: str) -> str:
        """Reject whitespace-only messages and store the trimmed body."""

        body = value.strip()
        if not body:
            raise ValueError("Message body cannot be empty.")
        return body


class ChatMessageListResponse(BaseModel):
    """Envelope for ``GET /api/chat/threads/{thread_id}/messages``."""

    data: list[ChatMessageRead]


class ChatMessageResponse(BaseModel):
    """Envelope for single-message responses."""

    data: ChatMessageRead
