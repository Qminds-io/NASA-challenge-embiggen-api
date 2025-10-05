from __future__ import annotations

from datetime import date as DateType
from typing import Dict, Optional, Protocol

import httpx
from fastapi import HTTPException, status

from app.cache import FileCache
from app.core.config import settings


class LayerDefinition(Protocol):
    layer_key: str
    title: str
    kind: str
    body: str
    projection: str
    matrix_set: Optional[str]
    image_format: Optional[str]
    style: Optional[str]
    max_zoom: Optional[int]
    default_date: Optional[DateType]
    source_template: str


class NasaBroadcast:
    """Cliente ligero para GIBS y Treks con cache local."""

    def __init__(
        self,
        cache: Optional[FileCache] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.cache = cache or FileCache(settings.tile_cache_dir, settings.tile_cache_ttl_seconds)
        self._client = client or httpx.AsyncClient(timeout=settings.http_timeout_seconds)
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def get_tile(
        self,
        layer: LayerDefinition,
        z: int,
        x: int,
        y: int,
        date_override: Optional[DateType] = None,
    ) -> tuple[bytes, Dict[str, str]]:
        cache_key = self._cache_key(layer, z, x, y, date_override)
        cached = self.cache.get(cache_key)
        if cached:
            return cached.body, dict(cached.headers)

        url = self._build_url(layer, z, x, y, date_override)
        try:
            response = await self._client.get(url)
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "status": "timeout",
                    "code": "nasa_timeout",
                    "message": "NASA tardo demasiado en responder",
                    "details": str(exc),
                },
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "status": "error",
                    "code": "nasa_connection_error",
                    "message": "No se pudo contactar a NASA",
                    "details": str(exc),
                },
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "status": "error",
                    "code": "nasa_bad_response",
                    "message": "NASA devolvio un error",
                    "details": {
                        "status_code": response.status_code,
                        "url": str(response.request.url),
                    },
                },
            )

        headers = {
            "Content-Type": response.headers.get("Content-Type", "image/png"),
            "Cache-Control": response.headers.get("Cache-Control", "public, max-age=3600"),
        }
        if etag := response.headers.get("ETag"):
            headers["ETag"] = etag
        if last_modified := response.headers.get("Last-Modified"):
            headers["Last-Modified"] = last_modified

        body = response.content
        self.cache.set(cache_key, body, headers)
        return body, headers

    def _cache_key(
        self,
        layer: LayerDefinition,
        z: int,
        x: int,
        y: int,
        date_override: Optional[DateType] = None,
    ) -> str:
        target_date = (date_override or layer.default_date or DateType.today()).isoformat()
        return f"{layer.layer_key}:{target_date}:{z}:{x}:{y}"

    def _build_url(
        self,
        layer: LayerDefinition,
        z: int,
        x: int,
        y: int,
        date_override: Optional[DateType] = None,
    ) -> str:
        if layer.kind == "gibs":
            return self._build_gibs(layer, z, x, y, date_override)
        if layer.kind == "trek":
            return self._build_treks(layer, z, x, y)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "code": "unknown_layer_kind",
                "message": f"Tipo de capa desconocido: {layer.kind}",
            },
        )

    def _build_gibs(
        self,
        layer: LayerDefinition,
        z: int,
        x: int,
        y: int,
        date_override: Optional[DateType],
    ) -> str:
        base_url = str(settings.nasa_gibs_base_url).rstrip("/")
        layer_id = layer.layer_key.split(":", 1)[1] if ":" in layer.layer_key else layer.layer_key
        matrix_set = layer.matrix_set or "GoogleMapsCompatible_Level9"
        image_format = layer.image_format or "jpg"
        target_date = (date_override or layer.default_date or DateType.today()).isoformat()
        template = layer.source_template or "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}"
        full_template = template if template.startswith("http") else f"{base_url}/{template.lstrip('/')}"
        return full_template.format(
            layerId=layer_id,
            date=target_date,
            matrixSet=matrix_set,
            z=z,
            y=y,
            x=x,
            format=image_format,
            style=layer.style or "default",
        )

    def _build_treks(
        self,
        layer: LayerDefinition,
        z: int,
        x: int,
        y: int,
    ) -> str:
        template = layer.source_template or "{body}/EQ/{layer}/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}"
        base_url = None if template.startswith("http") else str(settings.nasa_treks_base_url).rstrip("/")
        path = template if template.startswith("http") else f"{base_url}/{template.lstrip('/')}"
        matrix_set = layer.matrix_set or "default028mm"
        image_format = layer.image_format or "png"
        style = layer.style or "default"
        parts = layer.layer_key.split(":", 2)
        body_fragment = parts[1] if len(parts) > 1 else layer.body
        layer_fragment = parts[2] if len(parts) > 2 else layer.layer_key
        return path.format(
            body=body_fragment,
            layer=layer_fragment,
            style=style,
            matrixSet=matrix_set,
            z=z,
            y=y,
            x=x,
            format=image_format,
        )


def get_nasa_broadcast() -> NasaBroadcast:
    return nasa_broadcast


nasa_broadcast = NasaBroadcast()