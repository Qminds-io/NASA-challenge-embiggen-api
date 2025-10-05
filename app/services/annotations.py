
from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.annotations import AnnotationRepository, to_feature_list
from app.schemas import AnnotationBulkRequest, AnnotationBulkResponse


class AnnotationService:
    def __init__(self, db: Session) -> None:
        self.repo = AnnotationRepository(db)

    def query_annotations(self, payload: AnnotationBulkRequest) -> AnnotationBulkResponse:
        frame = payload.frame
        if payload.frame.extent:
            models = self.repo.list_in_bounds(
                frame.extent.min_lat,
                frame.extent.min_lon,
                frame.extent.max_lat,
                frame.extent.max_lon,
            )
        else:
            models = self.repo.list_all()
        return AnnotationBulkResponse(frame=frame, features=to_feature_list(models))

    def create_annotations(self, payload: AnnotationBulkRequest) -> AnnotationBulkResponse:
        created = self.repo.create_many(payload.frame, payload.features)
        return AnnotationBulkResponse(frame=payload.frame, features=to_feature_list(created))

    def delete_annotation(self, annotation_id: int) -> bool:
        return self.repo.delete(annotation_id)
