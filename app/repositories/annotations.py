from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.db import models
from app.schemas import Annotation


class AnnotationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def replace_for_session(
        self,
        session_model: models.SessionModel,
        annotations: Sequence[Annotation],
    ) -> list[models.AnnotationModel]:
        for existing in list(session_model.annotations):
            self.session.delete(existing)

        created: list[models.AnnotationModel] = []
        for annotation in annotations:
            model = models.AnnotationModel(
                session=session_model,
                order=annotation.order,
                feature=annotation.feature,
                properties=annotation.properties,
            )
            self.session.add(model)
            created.append(model)

        self.session.commit()
        for model in created:
            self.session.refresh(model)
        return created
