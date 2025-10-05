
from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.dependencies import limit_db_requests
from app.schemas import AnnotationBulkRequest, AnnotationBulkResponse
from app.services.annotations import AnnotationService

router = APIRouter(prefix="/v1/annotations", tags=["Annotations"])


def _service(db: Session) -> AnnotationService:
    return AnnotationService(db)


@router.post(
    "/query",
    response_model=AnnotationBulkResponse,
    summary="Consultar anotaciones dentro del frame dado",
)
def query_annotations(
    payload: AnnotationBulkRequest,
    _: None = Depends(limit_db_requests),
    db: Session = Depends(get_db),
) -> AnnotationBulkResponse:
    service = _service(db)
    return service.query_annotations(payload)


@router.post(
    "",
    response_model=AnnotationBulkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear anotaciones globales",
)
def create_annotations(
    payload: AnnotationBulkRequest,
    _: None = Depends(limit_db_requests),
    db: Session = Depends(get_db),
) -> AnnotationBulkResponse:
    service = _service(db)
    return service.create_annotations(payload)


@router.delete(
    "/{annotation_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar una anotacion",
)
def delete_annotation(
    annotation_id: int,
    secret: Optional[str] = Query(None, description="Codigo secreto requerido", alias="secret"),
    _: None = Depends(limit_db_requests),
    db: Session = Depends(get_db),
) -> dict:
    if not secret or secret != settings.annotation_delete_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": "forbidden",
                "code": "invalid_secret",
                "message": "Codigo secreto invalido.",
            },
        )
    service = _service(db)
    deleted = service.delete_annotation(annotation_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "not_found",
                "code": "annotation_not_found",
                "message": "La anotacion no existe.",
            },
        )
    return {"status": "deleted"}
