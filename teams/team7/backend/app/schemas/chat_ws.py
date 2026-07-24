"""Pydantic schemas for the Chat WebSocket protocol (SCRUM-11).

The wire format mirrors the contract documented in
``teams/team7/.agents/04_api_endpoints.md`` §1.2:

- Client → server envelopes carry an ``op`` and operation-specific fields.
- Server → client envelopes carry an ``event`` and a ``data`` payload.

We deliberately keep these schemas independent of the SQLAlchemy ORM
models so the wire contract can evolve without churning persistence.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Client → server
# ---------------------------------------------------------------------------


class WsSendMessage(BaseModel):
    """``op: send`` — persist and broadcast a text message."""

    op: Literal["send"]
    body: str = Field(min_length=1, max_length=8000)


class WsTypingEvent(BaseModel):
    """``op: typing`` — broadcast a typing indicator."""

    op: Literal["typing"]
    is_typing: bool


class WsReadEvent(BaseModel):
    """``op: read`` — mark a message as read by the current caller."""

    op: Literal["read"]
    message_id: int = Field(gt=0)


class WsClientEnvelope(BaseModel):
    """Discriminator union for client-to-server messages.

    FastAPI / Pydantic v2 resolves the concrete subtype from the ``op``
    field; ``WsClientEnvelope`` is only used for documentation and
    service-layer typing.
    """

    model_config = ConfigDict(extra="forbid")

    op: Literal["send", "typing", "read"]


# ---------------------------------------------------------------------------
# Server → client
# ---------------------------------------------------------------------------


class WsMessageData(BaseModel):
    """Payload for ``message.created`` events."""

    id: int
    thread_id: int
    sender_user_id: int
    body: str
    sent_at: datetime


class WsReadData(BaseModel):
    """Payload for ``message.read`` events."""

    message_id: int
    thread_id: int
    reader_user_id: int
    read_at: datetime


class WsTypingData(BaseModel):
    """Payload for ``typing.start`` / ``typing.stop`` events."""

    thread_id: int
    user_id: int
    is_typing: bool


class WsPresenceData(BaseModel):
    """Payload for ``presence.update`` events."""

    coach_user_id: int
    is_online: bool
