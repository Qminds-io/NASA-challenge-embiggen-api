
from __future__ import annotations

from datetime import date as DateType
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.annotations import AnnotationRepository, to_feature_list
from app.schemas import AnnotationBulkRequest, AnnotationBulkResponse


class AnnotationService:
    def __init__(self, db: Session) -> None:
        self.repo = AnnotationRepository(db)

    def query_annotations(self, payload: AnnotationBulkRequest) -> AnnotationBulkResponse:
        frame = payload.frame
        extent = frame.extent
        models = self.repo.list_filtered(
            south=extent.min_lat if extent else None,
            west=extent.min_lon if extent else None,
            north=extent.max_lat if extent else None,
            east=extent.max_lon if extent else None,
            layer_key=frame.layer_key,
            projection=frame.projection,
            date=frame.date,
        )
        return AnnotationBulkResponse(frame=frame, features=to_feature_list(models))

    def list_annotations_with_params(
        self,
        layer_key: Optional[str],
        projection: Optional[str],
        date: Optional[DateType],
        zoom: Optional[float],
        opacity: Optional[float],
        center_lat: Optional[float],
        center_lon: Optional[float],
        min_lat: Optional[float],
        min_lon: Optional[float],
        max_lat: Optional[float],
        max_lon: Optional[float],
        limit: Optional[int],
    ):
        models = self.repo.list_filtered(
            south=min_lat,
            west=min_lon,
            north=max_lat,
            east=max_lon,
            layer_key=layer_key,
            projection=projection,
            date=date,
            limit=limit,
        )
        return to_feature_list(models)

    def create_annotations(self, payload: AnnotationBulkRequest) -> AnnotationBulkResponse:
        created = self.repo.create_many(payload.frame, payload.features)
        return AnnotationBulkResponse(frame=payload.frame, features=to_feature_list(created))

    def delete_annotation(self, annotation_id: int) -> bool:
        return self.repo.delete(annotation_id)
