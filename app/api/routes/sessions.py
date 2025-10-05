from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import limit_db_requests
from app.schemas import (
    AnnotationUpsertRequest,
    Session as SessionSchema,
    SessionCreateRequest,
    SessionUpdateRequest,
)
from app.services.sessions import SessionService

router = APIRouter(prefix="/v1/sessions", tags=["Sessions"])


def _service(db: Session) -> SessionService:
    return SessionService(db)


@router.get("", response_model=List[SessionSchema], summary="Listar sesiones recientes")
def list_sessions(
    _: None = Depends(limit_db_requests),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> List[SessionSchema]:
    service = _service(db)
    return service.list_recent(limit)


@router.post(
    "",
    response_model=SessionSchema,
    status_code=201,
    summary="Crear nueva sesion",
)
def create_session(
    payload: SessionCreateRequest,
    _: None = Depends(limit_db_requests),
    db: Session = Depends(get_db),
) -> SessionSchema:
    service = _service(db)
    return service.create_session(payload)


@router.put("/{session_id}", response_model=SessionSchema, summary="Actualizar una sesion")
def update_session(
    payload: SessionUpdateRequest,
    session_id: int = Path(..., ge=1),
    _: None = Depends(limit_db_requests),
    db: Session = Depends(get_db),
) -> SessionSchema:
    service = _service(db)
    return service.update_session(session_id, payload)


@router.post(
    "/{session_id}/annotations",
    summary="Reemplazar anotaciones de una sesion",
)
def replace_annotations(
    payload: AnnotationUpsertRequest,
    session_id: int = Path(..., ge=1),
    _: None = Depends(limit_db_requests),
    db: Session = Depends(get_db),
) -> dict:
    service = _service(db)
    session = service.replace_annotations(session_id, payload.features)
    return {
        "type": "FeatureCollection",
        "features": [annotation.feature for annotation in session.annotations],
    }
