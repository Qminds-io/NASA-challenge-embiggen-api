from __future__ import annotations

from datetime import date as DateType
from typing import Optional, Tuple

from fastapi import HTTPException, status

from app.broadcast.nasa import NasaBroadcast
from app.layers_catalog import get_layer


class TileService:
    def __init__(self, broadcast: NasaBroadcast) -> None:
        self.broadcast = broadcast

    async def fetch_tile(
        self,
        layer_key: str,
        z: int,
        x: int,
        y: int,
        date_override: Optional[DateType],
    ) -> Tuple[bytes, dict[str, str]]:
        layer = get_layer(layer_key)
        if layer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "not_found",
                    "code": "layer_not_found",
                    "message": f"La capa '{layer_key}' no esta registrada.",
                },
            )
        if layer.kind == "gibs" and not (date_override or layer.default_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "invalid",
                    "code": "missing_date",
                    "message": "Las capas GIBS requieren fecha (query ?date=YYYY-MM-DD).",
                },
            )
        return await self.broadcast.get_tile(layer, z, x, y, date_override)