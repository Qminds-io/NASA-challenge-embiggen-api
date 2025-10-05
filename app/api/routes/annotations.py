from __future__ import annotations

from datetime import date as DateType
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.dependencies import limit_db_requests
from app.schemas import (
    AnnotationBulkRequest,
    AnnotationBulkResponse,
    Frame,
    FrameCenter,
    FrameExtent,
)
from app.services.annotations import AnnotationService

router = APIRouter(prefix="/v1/annotations", tags=["Annotations"])


def _service(db: Session) -> AnnotationService:
    return AnnotationService(db)


@router.get(
    "",
    response_model=AnnotationBulkResponse,
    summary="Consultar anotaciones utilizando parametros del mapa",
)
def list_annotations(
    layer_key: str = Query(..., alias="layerKey", description="Identificador de la capa"),
    projection: str = Query(..., description="Proyeccion activa"),
    zoom: float = Query(..., description="Nivel de zoom actual"),
    opacity: float = Query(1.0, description="Opacidad aplicada a la capa"),
    center_lon: float = Query(..., alias="centerLon", description="Longitud del centro"),
    center_lat: float = Query(..., alias="centerLat", description="Latitud del centro"),
    min_lon: float = Query(..., alias="minLon", description="Longitud minima del cuadro"),
    min_lat: float = Query(..., alias="minLat", description="Latitud minima del cuadro"),
    max_lon: float = Query(..., alias="maxLon", description="Longitud maxima del cuadro"),
    max_lat: float = Query(..., alias="maxLat", description="Latitud maxima del cuadro"),
    date: Optional[DateType] = Query(None, description="Fecha asociada a la capa"),
    limit: Optional[int] = Query(None, ge=1, description="Limite de anotaciones devueltas"),
    _: None = Depends(limit_db_requests),
    db: Session = Depends(get_db),
) -> AnnotationBulkResponse:
    frame = Frame(
        layer_key=layer_key,
        date=date,
        projection=projection,
        zoom=zoom,
        opacity=opacity,
        center=FrameCenter(lon=center_lon, lat=center_lat),
        extent=FrameExtent(
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
        ),
    )
    service = _service(db)
    return service.query_by_frame(frame, limit=limit)


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
