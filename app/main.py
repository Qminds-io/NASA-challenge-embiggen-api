from __future__ import annotations

from contextlib import closing

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import health, layers, sessions, tiles
from app.broadcast.nasa import get_nasa_broadcast
from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.layers import LayerRepository, default_layers

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API privada para el visor NASA Embiggen.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def enforce_allowed_origin(request: Request, call_next):
    allowed = set(settings.allowed_origins)
    if "*" not in allowed and request.url.path not in {"/", "/api/health"}:
        origin = request.headers.get("origin")
        if origin not in allowed:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "status": "forbidden",
                    "code": "origin_not_allowed",
                    "message": "Dominio no autorizado para consumir esta API.",
                },
            )
    return await call_next(request)
app.include_router(health.router, prefix="/api")
app.include_router(layers.router)
app.include_router(tiles.router)
app.include_router(sessions.router)


@app.on_event("startup")
async def startup_event() -> None:
    with closing(SessionLocal()) as db:
        repo = LayerRepository(db)
        repo.ensure_seeded(default_layers())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await get_nasa_broadcast().close()


@app.get("/", tags=["Health"])
def read_root() -> dict[str, str]:
    return {"app": settings.app_name, "environment": settings.environment}


__all__ = ["app"]
