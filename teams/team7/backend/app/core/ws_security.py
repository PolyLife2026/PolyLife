"""WebSocket-aware identity helpers.

The team gateway already authenticates the request via Nginx
``auth_request`` and forwards the resolved identity as
``X-User-Id`` / ``X-User-Username`` headers (see ``teams/team7/gateway.conf``).
Those headers are also forwarded on the WebSocket Upgrade request, so the
backend can read them before ``websocket.accept()`` without decoding any
JWT itself.

``get_current_user_for_ws`` is a thin adapter that mirrors the
REST ``get_current_user`` dependency but accepts a raw ``WebSocket`` so it
can be called inside a handler before ``accept()``. On failure it raises
``WebSocketException`` with the standard 1008 (policy violation) close
code so the framework sends a proper close frame without upgrading the
connection.
"""

from __future__ import annotations

from fastapi import WebSocket, status
from fastapi.exceptions import WebSocketException

from app.core.security import CurrentUser


def get_current_user_for_ws(websocket: WebSocket) -> CurrentUser:
    """Read ``X-User-*`` headers from the WebSocket scope and return a ``CurrentUser``.

    Mirrors ``app.core.security.get_current_user`` but raises
    ``WebSocketException(1008)`` instead of ``HTTPException(401)`` so the
    upgrade is rejected cleanly.
    """
    x_user_id = websocket.headers.get("X-User-Id")
    x_user_username = websocket.headers.get("X-User-Username")
    if not x_user_id or not x_user_username:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing forwarded identity headers from the gateway.",
        )
    try:
        user_id = int(x_user_id)
    except ValueError as exc:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Malformed X-User-Id header (not an integer).",
        ) from exc
    return CurrentUser(id=user_id, username=x_user_username)
