from __future__ import annotations

from typing import Iterable, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.annotations import AnnotationRepository
from app.repositories.layers import LayerRepository
from app.repositories.sessions import SessionRepository
from app.schemas import Annotation, MapState, Session as SessionSchema, SessionCreateRequest, SessionUpdateRequest


class SessionService:
    def __init__(self, db: Session) -> None:
        self.layers = LayerRepository(db)
        self.sessions = SessionRepository(db)
        self.annotations = AnnotationRepository(db)

    def list_recent(self, limit: int = 50) -> List[SessionSchema]:
        rows = self.sessions.list_recent(limit)
        return [self._to_schema(row) for row in rows]

    def create_session(
        self,
        payload: SessionCreateRequest,
        user_id: Optional[int] = None,
    ) -> SessionSchema:
        self._ensure_layer(payload.state.layer_key)
        session_model = self.sessions.create(payload.state, user_id=user_id)
        if payload.annotations:
            self.annotations.replace_for_session(session_model, payload.annotations)
            session_model = self.sessions.get(session_model.id)
            assert session_model is not None
        return self._to_schema(session_model)

    def update_session(
        self,
        session_id: int,
        payload: SessionUpdateRequest,
    ) -> SessionSchema:
        session_model = self.sessions.get(session_id)
        if session_model is None:
            raise self._not_found(session_id)
        self._ensure_layer(payload.state.layer_key)
        session_model = self.sessions.update_state(session_model, payload.state)
        if payload.annotations is not None:
            self.annotations.replace_for_session(session_model, payload.annotations)
            session_model = self.sessions.get(session_id)
            assert session_model is not None
        return self._to_schema(session_model)

    def replace_annotations(
        self,
        session_id: int,
        annotations: Iterable[Annotation],
    ) -> SessionSchema:
        session_model = self.sessions.get(session_id)
        if session_model is None:
            raise self._not_found(session_id)
        self.annotations.replace_for_session(session_model, list(annotations))
        session_model = self.sessions.get(session_id)
        assert session_model is not None
        return self._to_schema(session_model)

    def _ensure_layer(self, layer_key: str) -> None:
        if self.layers.get_by_key(layer_key) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "not_found",
                    "code": "layer_not_found",
                    "message": f"La capa '{layer_key}' no esta registrada.",
                },
            )

    @staticmethod
    def _to_schema(model) -> SessionSchema:
        state = MapState(
            lon=model.lon,
            lat=model.lat,
            zoom=model.zoom,
            date=model.date,
            layer_key=model.layer_key,
            projection=model.projection,
            opacity=model.opacity,
        )
        annotations = [
            Annotation(
                id=item.id,
                session_id=item.session_id,
                feature=item.feature,
                order=item.order,
                properties=item.properties,
            )
            for item in model.annotations
        ]
        return SessionSchema(
            id=model.id,
            state=state,
            annotations=annotations,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at or model.created_at,
        )

    @staticmethod
    def _not_found(session_id: int) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "not_found",
                "code": "session_not_found",
                "message": f"La sesion {session_id} no existe.",
            },
        )
