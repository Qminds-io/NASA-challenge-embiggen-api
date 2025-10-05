from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Service health check")
async def healthcheck() -> dict[str, str]:
    """Return a canned response so App Runner can probe the service."""
    return {"status": "ok"}
