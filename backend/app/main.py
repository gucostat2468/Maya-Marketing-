"""Ponto de entrada do backend local da Maya-marketing."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import backups, dashboard, integrations, system
from app.core.config import APP_NAME, APP_VERSION, get_settings
from app.core.logging import configure_logging
from app.db.migrate import upgrade_to_head
from app.db.session import get_db
from app.services.seed import seed_reference_data

log = logging.getLogger("maya")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_dir, settings.log_level)
    upgrade_to_head()
    db = next(get_db())
    try:
        seed_reference_data(db)
    finally:
        db.close()
    log.info("Maya-marketing %s iniciada (workspace=%s)", APP_VERSION, settings.workspace)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=f"{APP_NAME} API", version=APP_VERSION, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(Exception)
    async def unhandled(_request: Request, exc: Exception) -> JSONResponse:
        log.exception("Erro não tratado: %s", type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno no backend. Detalhes técnicos foram gravados no log."},
        )

    for router in (system.router, dashboard.router, integrations.router, backups.router):
        app.include_router(router, prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    s = get_settings()
    uvicorn.run("app.main:app", host=s.host, port=s.port)
