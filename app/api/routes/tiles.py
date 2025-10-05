from __future__ import annotations

from datetime import date as DateType
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.broadcast.nasa import get_nasa_broadcast
from app.db.session import get_db
from app.services.tiles import TileService

router = APIRouter(prefix="/v1/layers", tags=["Tiles"])


@router.get("/{layer_key}/tiles/{z}/{x}/{y}", summary="Proxy sencillo hacia NASA")
async def proxy_tile(
    layer_key: str,
    z: int = Path(..., ge=0, description="Zoom"),
    x: int = Path(..., ge=0, description="Tile column"),
    y: int = Path(..., ge=0, description="Tile row"),
    date_param: Optional[DateType] = Query(None, alias="date", description="Fecha YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    service = TileService(db, get_nasa_broadcast())
    body, headers = await service.fetch_tile(layer_key, z, x, y, date_param)
    response = Response(content=body, media_type=headers.get("Content-Type", "image/png"))
    for header in ("Cache-Control", "ETag", "Last-Modified"):
        if header in headers:
            response.headers[header] = headers[header]
    return response
