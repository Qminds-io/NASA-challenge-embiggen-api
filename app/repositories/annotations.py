
from __future__ import annotations

from collections.abc import Sequence
from typing import Optional

from sqlalchemy import and_, between, select
from sqlalchemy.orm import Session

from app.db import models
from app.schemas import AnnotationFeature, AnnotationFeaturePayload, Frame


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
        for feature_payload in features:
            geometry = feature_payload.feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [0, 0])
            lon, lat = coordinates
            model = models.AnnotationModel(
                external_id=feature_payload.id,
                order=feature_payload.order,
                feature=feature_payload.feature,
                properties=feature_payload.properties,
                title=feature_payload.feature.get("properties", {}).get("name", feature_payload.feature.get("id", "Annotation")),
                description=feature_payload.feature.get("properties", {}).get("description"),
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

    def list_all(self) -> list[models.AnnotationModel]:
        stmt = select(models.AnnotationModel).order_by(models.AnnotationModel.updated_at.desc())
        return self.session.execute(stmt).scalars().all()

    def list_in_bounds(
        self,
        south: float,
        west: float,
        north: float,
        east: float,
    ) -> list[models.AnnotationModel]:
        stmt = (
            select(models.AnnotationModel)
            .where(
                and_(
                    between(models.AnnotationModel.lat, south, north),
                    between(models.AnnotationModel.lon, west, east),
                )
            )
            .order_by(models.AnnotationModel.updated_at.desc())
        )
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
