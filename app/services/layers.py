from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.layers_catalog import all_layers
from app.schemas import Layer


class LayerService:
    def grouped_by_body(self) -> Dict[str, List[Layer]]:
        catalog = defaultdict(list)
        for config in all_layers().values():
            template = f"/v1/layers/{config.layer_key}/tiles/{{z}}/{{x}}/{{y}}"
            if config.kind == "gibs":
                template += "?date={date}"
            catalog[config.body].append(
                Layer(
                    layer_key=config.layer_key,
                    title=config.title,
                    kind=config.kind,  # type: ignore[arg-type]
                    body=config.body,
                    projection=config.projection,
                    matrix_set=config.matrix_set,
                    image_format=config.image_format,
                    tile_template=template,
                    max_zoom=config.max_zoom,
                    default_date=config.default_date,
                )
            )
        return dict(catalog)