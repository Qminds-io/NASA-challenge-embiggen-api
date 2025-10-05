from __future__ import annotations

from typing import List, Optional

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
