from __future__ import annotations

from datetime import date as DateType
from typing import Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models
from app.schemas import Layer


class LayerRepository:
    """Consultas y comandos sobre la tabla de capas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> List[Layer]:
        stmt = select(models.LayerModel).order_by(models.LayerModel.body, models.LayerModel.title)
        rows = self.session.execute(stmt).scalars().all()
        return [self._to_schema(row) for row in rows]

    def get_by_key(self, layer_key: str) -> Optional[models.LayerModel]:
        stmt = select(models.LayerModel).where(models.LayerModel.layer_key == layer_key)
        return self.session.execute(stmt).scalar_one_or_none()

    def ensure_seeded(self, definitions: Iterable[models.LayerModel]) -> None:
        if self.session.execute(select(models.LayerModel.id)).first() is None:
            self.session.add_all(definitions)
            self.session.commit()

    @staticmethod
    def _to_schema(row: models.LayerModel) -> Layer:
        template = f"/v1/layers/{row.layer_key}/tiles/{{z}}/{{x}}/{{y}}"
        if row.kind == "gibs":
            template += "?date={date}"
        return Layer(
            layer_key=row.layer_key,
            title=row.title,
            kind=row.kind,  # type: ignore[arg-type]
            body=row.body,
            projection=row.projection,
            matrix_set=row.matrix_set,
            image_format=row.image_format,
            tile_template=template,
            max_zoom=row.max_zoom,
            default_date=row.default_date,
        )


def default_layers() -> List[models.LayerModel]:
    return [
        models.LayerModel(
            layer_key="gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
            title="MODIS Terra True Color",
            kind="gibs",
            body="earth",
            projection="EPSG:3857",
            matrix_set="GoogleMapsCompatible_Level9",
            image_format="jpg",
            style="default",
            max_zoom=9,
            default_date=DateType(2024, 1, 1),
            source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
        ),
        models.LayerModel(
            layer_key="trek:Moon:LRO_LOLA_ClrShade_Global_128ppd_v04",
            title="LRO LOLA Color Shaded Relief",
            kind="trek",
            body="moon",
            projection="EPSG:4326",
            matrix_set="default028mm",
            image_format="png",
            style="default",
            max_zoom=8,
            source_template="{body}/EQ/{layer}/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
        ),
        models.LayerModel(
            layer_key="trek:Mars:CTX_Mosaic_Global_6ppd",
            title="CTX Global Mosaic",
            kind="trek",
            body="mars",
            projection="EPSG:4326",
            matrix_set="default028mm",
            image_format="png",
            style="default",
            max_zoom=9,
            source_template="{body}/EQ/{layer}/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
        ),
    ]
