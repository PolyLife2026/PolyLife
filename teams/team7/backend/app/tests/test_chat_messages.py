"""REST chat message history and sending tests."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.models.chat_thread import ChatThread

USER = {"X-User-Id": "42", "X-User-Username": "alice"}
COACH = {"X-User-Id": "101", "X-User-Username": "coach"}
STRANGER = {"X-User-Id": "99", "X-User-Username": "mallory"}


async def _make_thread(
    db_session: AsyncSession,
    make_coach,  # type: ignore[no-untyped-def]
) -> ChatThread:
    coach = await make_coach(user_id=int(COACH["X-User-Id"]))
    thread = ChatThread(
        user_id=int(USER["X-User-Id"]),
        coach_user_id=coach.user_id,
    )
    db_session.add(thread)
    await db_session.commit()
    await db_session.refresh(thread)
    return thread


async def test_thread_participant_can_send_and_list_messages(
    client: AsyncClient,
    db_session: AsyncSession,
    override_db: AsyncSession,  # noqa: ARG001
    make_coach,  # type: ignore[no-untyped-def]
) -> None:
    """User and coach messages persist and are returned chronologically."""

    thread = await _make_thread(db_session, make_coach)

    first = await client.post(
        f"/chat/threads/{thread.id}/messages",
        json={"body": "  Hello coach  "},
        headers=USER,
    )
    second = await client.post(
        f"/chat/threads/{thread.id}/messages",
        json={"body": "Hello! How can I help?"},
        headers=COACH,
    )

    assert first.status_code == 201
    assert first.json()["data"]["body"] == "Hello coach"
    assert first.json()["data"]["sender_user_id"] == int(USER["X-User-Id"])
    assert second.status_code == 201
    assert second.json()["data"]["sender_user_id"] == int(COACH["X-User-Id"])

    history = await client.get(
        f"/chat/threads/{thread.id}/messages",
        headers=USER,
    )
    assert history.status_code == 200
    assert [row["body"] for row in history.json()["data"]] == [
        "Hello coach",
        "Hello! How can I help?",
    ]


async def test_send_message_rejects_blank_body(
    client: AsyncClient,
    db_session: AsyncSession,
    override_db: AsyncSession,  # noqa: ARG001
    make_coach,  # type: ignore[no-untyped-def]
) -> None:
    """Whitespace-only messages fail validation."""

    thread = await _make_thread(db_session, make_coach)
    response = await client.post(
        f"/chat/threads/{thread.id}/messages",
        json={"body": "   "},
        headers=USER,
    )
    assert response.status_code == 422


async def test_non_participant_cannot_read_or_send_messages(
    client: AsyncClient,
    db_session: AsyncSession,
    override_db: AsyncSession,  # noqa: ARG001
    make_coach,  # type: ignore[no-untyped-def]
) -> None:
    """A caller outside the user/coach pair receives 403."""

    thread = await _make_thread(db_session, make_coach)

    history = await client.get(
        f"/chat/threads/{thread.id}/messages",
        headers=STRANGER,
    )
    sent = await client.post(
        f"/chat/threads/{thread.id}/messages",
        json={"body": "I should not be here"},
        headers=STRANGER,
    )

    assert history.status_code == 403
    assert sent.status_code == 403


async def test_message_history_excludes_soft_deleted_rows(
    client: AsyncClient,
    db_session: AsyncSession,
    override_db: AsyncSession,  # noqa: ARG001
    make_coach,  # type: ignore[no-untyped-def]
) -> None:
    """Soft-deleted messages do not appear in history."""

    thread = await _make_thread(db_session, make_coach)
    db_session.add_all(
        [
            ChatMessage(
                thread_id=thread.id,
                sender_user_id=int(USER["X-User-Id"]),
                body="Visible",
            ),
            ChatMessage(
                thread_id=thread.id,
                sender_user_id=int(USER["X-User-Id"]),
                body="Hidden",
                is_deleted=True,
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(
        f"/chat/threads/{thread.id}/messages",
        headers=USER,
    )
    assert response.status_code == 200
    assert [row["body"] for row in response.json()["data"]] == ["Visible"]
