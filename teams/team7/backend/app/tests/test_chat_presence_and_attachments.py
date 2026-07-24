"""SCRUM-14 smoke tests for chat presence."""

from __future__ import annotations

from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coach_profile import CoachProfile

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
