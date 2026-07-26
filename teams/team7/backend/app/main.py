"""FastAPI application factory.

Sprint 1 skeleton: a single `/healthz` endpoint and permissive CORS for
local dev. Chat + reserve routers are wired in their own tickets
(`SCRUM-8`, `SCRUM-9`, etc.). The WebSocket router and Redis lifespan
were added in `SCRUM-11`.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.chat_ws import router as chat_ws_router
from app.api.meta import router as meta_router
from app.api.reserve import router as reserve_router
from app.core.config import settings
from app.core.redis import close_redis_client, init_redis_client

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(_application: FastAPI) -> AsyncIterator[None]:
    """Initialise the shared Redis client on startup; close it on shutdown."""
    init_redis_client()
    logger.info("Shared Redis client initialised: %s", settings.url_redis)
    try:
        yield
    finally:
        await close_redis_client()
        logger.info("Shared Redis client closed.")


def create_app() -> FastAPI:
    """Build the FastAPI app instance."""
    application = FastAPI(
        title="PolyLife Team 7 — Chat & Reserve",
        version="0.1.0",
        description=(
            "Chat with Coach + Reserve Coach microservices. "
            "Owned by PolyLife Team 7 (Sina Sadeghi, Sina Negahban, Amirali Rahimi)."
        ),
        lifespan=_lifespan,
    )

    # Permissive CORS for local dev. Tighten before any production deploy.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(chat_router)
    application.include_router(chat_ws_router)
    application.include_router(meta_router)
    application.include_router(reserve_router)

    @application.get("/healthz", tags=["meta"])
    async def healthz() -> dict[str, str]:
        """Liveness probe. Returns 200 as long as the process is up."""
        return {"status": "ok"}

    return application


app = create_app()
