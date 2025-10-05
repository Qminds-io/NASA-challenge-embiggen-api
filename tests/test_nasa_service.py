from __future__ import annotations

from datetime import date as DateType

import httpx
import pytest

from app.broadcast.nasa import NasaBroadcast
from app.cache import FileCache
from app.db.models import LayerModel


@pytest.mark.asyncio
async def test_gibs_tile_fetch_and_cache(tmp_path, respx_mock):
    cache = FileCache(tmp_path, ttl_seconds=60)
    service = NasaBroadcast(cache=cache)
    layer = LayerModel(
        layer_key="gibs:TEST_LAYER",
        title="Test Layer",
        kind="gibs",
        body="earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level9",
        image_format="png",
        style="default",
        max_zoom=9,
        default_date=DateType(2024, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    )

    expected_url = service._build_gibs(layer, z=2, x=1, y=3, date_override=DateType(2024, 1, 5))
    respx_mock.get(expected_url).mock(
        return_value=httpx.Response(
            status_code=200,
            content=b"tile-bytes",
            headers={"Content-Type": "image/png", "Cache-Control": "max-age=60"},
        )
    )

    body, headers = await service.get_tile(layer, z=2, x=1, y=3, date_override=DateType(2024, 1, 5))
    assert body == b"tile-bytes"
    assert headers["Content-Type"] == "image/png"
    assert respx_mock.calls.call_count == 1

    cached_body, _ = await service.get_tile(layer, z=2, x=1, y=3, date_override=DateType(2024, 1, 5))
    assert cached_body == b"tile-bytes"
    assert respx_mock.calls.call_count == 1

    await service.close()
