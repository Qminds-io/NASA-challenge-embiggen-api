
from __future__ import annotations

from collections.abc import Sequence
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db import models
from app.schemas import AnnotationFeature, AnnotationFeaturePayload, Frame

def _flatten_positions(value: object) -> list[tuple[float, float]]:
    positions: list[tuple[float, float]] = []
    if isinstance(value, (list, tuple)):
        if value and isinstance(value[0], (int, float)):
            lon = float(value[0])
            lat = float(value[1]) if len(value) > 1 else 0.0
            positions.append((lon, lat))
        else:
            for item in value:
                positions.extend(_flatten_positions(item))
    return positions


def representative_point_from_geometry(geometry: object) -> tuple[float, float]:
    if not isinstance(geometry, dict):
        return 0.0, 0.0
    positions = _flatten_positions(geometry.get("coordinates"))
    if not positions:
        return 0.0, 0.0
    lon_total = sum(lon for lon, _ in positions)
    lat_total = sum(lat for _, lat in positions)
    count = len(positions)
    return lon_total / count, lat_total / count

class AnnotationRepository:
    """Persistence gateway for global annotations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_many(
        self,
        frame: Frame,
        features: Sequence[AnnotationFeaturePayload],
    ) -> list[models.AnnotationModel]:
        created: list[models.AnnotationModel] = []
        for payload in features:
            geometry = payload.feature.get("geometry", {})
            lon, lat = representative_point_from_geometry(geometry)
            model = models.AnnotationModel(
                external_id=payload.id,
                order=payload.order,
                feature=payload.feature,
                properties=payload.properties,
                title=payload.feature.get("properties", {}).get(
                    "name",
                    payload.feature.get("id", "Annotation"),
                ),
                description=payload.feature.get("properties", {}).get("description"),
                lat=lat,
                lon=lon,
                layer_key=frame.layer_key,
                date=frame.date,
                projection=frame.projection,
                zoom=frame.zoom,
                opacity=frame.opacity,
                center_lat=frame.center.lat,
                center_lon=frame.center.lon,
                extent_min_lat=frame.extent.min_lat,
                extent_min_lon=frame.extent.min_lon,
                extent_max_lat=frame.extent.max_lat,
                extent_max_lon=frame.extent.max_lon,
            )
            self.session.add(model)
            created.append(model)
        self.session.commit()
        for model in created:
            self.session.refresh(model)
        return created

    def delete(self, annotation_id: int) -> bool:
        stmt = select(models.AnnotationModel).where(models.AnnotationModel.id == annotation_id)
        instance = self.session.execute(stmt).scalar_one_or_none()
        if instance is None:
            return False
        self.session.delete(instance)
        self.session.commit()
        return True

    def list_filtered(
        self,
        *,
        south: Optional[float] = None,
        west: Optional[float] = None,
        north: Optional[float] = None,
        east: Optional[float] = None,
        layer_key: Optional[str] = None,
        projection: Optional[str] = None,
        date: Optional[object] = None,
        limit: Optional[int] = None,
    ) -> list[models.AnnotationModel]:
        stmt = select(models.AnnotationModel)
        conditions = []

        if None not in (south, north):
            south_val = min(south, north)  # type: ignore[arg-type]
            north_val = max(south, north)  # type: ignore[arg-type]
            conditions.append(models.AnnotationModel.lat.between(south_val, north_val))
        if None not in (west, east):
            west_val = min(west, east)  # type: ignore[arg-type]
            east_val = max(west, east)  # type: ignore[arg-type]
            conditions.append(models.AnnotationModel.lon.between(west_val, east_val))
        if layer_key:
            conditions.append(models.AnnotationModel.layer_key == layer_key)
        if projection:
            conditions.append(models.AnnotationModel.projection == projection)
        if date:
            conditions.append(models.AnnotationModel.date == date)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(models.AnnotationModel.updated_at.desc())
        if limit:
            stmt = stmt.limit(limit)
        return self.session.execute(stmt).scalars().all()


def to_feature(model: models.AnnotationModel) -> AnnotationFeature:
    return AnnotationFeature(
        id=str(model.id),
        order=model.order,
        feature=model.feature,
        properties=model.properties,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_feature_list(models_: Sequence[models.AnnotationModel]) -> list[AnnotationFeature]:
    return [to_feature(model) for model in models_]

