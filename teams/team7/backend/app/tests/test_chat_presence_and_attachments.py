"""SCRUM-14 / SCRUM-15 smoke tests for chat presence and attachments."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.models.chat_thread import ChatThread
from app.models.coach_profile import CoachProfile
from app.models.message_attachment import MessageAttachment

USER = {"X-User-Id": "42", "X-User-Username": "alice"}
COACH = {"X-User-Id": "101", "X-User-Username": "coach-bob"}


async def _add_coach(
    db_session: AsyncSession,
    *,
    user_id: int,
    is_online: bool = False,
) -> CoachProfile:
    row = CoachProfile(
        user_id=user_id,
        hourly_rate=Decimal("50.00"),
        is_online=is_online,
    )
    db_session.add(row)
    await db_session.flush()
    return row


async def _add_thread(
    db_session: AsyncSession,
    *,
    user_id: int,
    coach_user_id: int,
) -> ChatThread:
    row = ChatThread(user_id=user_id, coach_user_id=coach_user_id)
    db_session.add(row)
    await db_session.flush()
    return row


async def test_list_online_coaches_returns_only_online(
    client: AsyncClient,
    db_session: AsyncSession,
    override_db: AsyncSession,  # noqa: ARG001
) -> None:
    await _add_coach(db_session, user_id=101, is_online=True)
    await _add_coach(db_session, user_id=102, is_online=False)
    await db_session.commit()

    response = await client.get("/chat/coaches/online", headers=USER)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["user_id"] == 101
    assert data[0]["is_online"] is True


async def test_update_my_online_status_toggles_profile(
    client: AsyncClient,
    db_session: AsyncSession,
    override_db: AsyncSession,  # noqa: ARG001
) -> None:
    await _add_coach(db_session, user_id=101, is_online=False)
    await db_session.commit()

    response = await client.patch(
        "/chat/coaches/me/status",
        json={"is_online": True},
        headers=COACH,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_online"] is True

    refreshed = await db_session.execute(
        CoachProfile.__table__.select().where(CoachProfile.user_id == 101)
    )
    row = refreshed.mappings().one()
    assert row["is_online"] is True


async def test_upload_thread_attachment_creates_message_and_attachment(
    client: AsyncClient,
    db_session: AsyncSession,
    override_db: AsyncSession,  # noqa: ARG001
) -> None:
    await _add_coach(db_session, user_id=101)
    thread = await _add_thread(db_session, user_id=42, coach_user_id=101)
    await db_session.commit()

    response = await client.post(
        f"/chat/threads/{thread.id}/attachments",
        headers=USER,
        files={"file": ("note.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 201
    payload = response.json()["data"]
    assert payload["message_id"] > 0
    assert payload["size_bytes"] == 11
    assert payload["mime_type"] == "text/plain"
    assert payload["file_url"].startswith("file://")

    message_rows = await db_session.execute(ChatMessage.__table__.select())
    attachment_rows = await db_session.execute(MessageAttachment.__table__.select())
    assert len(message_rows.fetchall()) == 1
    assert len(attachment_rows.fetchall()) == 1

    stored_path = Path(payload["file_url"].removeprefix("file://"))
    assert stored_path.exists()
    stored_path.unlink()
