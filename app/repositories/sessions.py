from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import models
from app.schemas import MapState


class SessionRepository:
    """Operaciones CRUD para sesiones."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_recent(self, limit: int = 50) -> list[models.SessionModel]:
        stmt = (
            select(models.SessionModel)
            .options(selectinload(models.SessionModel.annotations))
            .order_by(models.SessionModel.updated_at.desc())
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()

    def get(self, session_id: int) -> Optional[models.SessionModel]:
        stmt = (
            select(models.SessionModel)
            .options(selectinload(models.SessionModel.annotations))
            .where(models.SessionModel.id == session_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, state: MapState, user_id: int | None = None) -> models.SessionModel:
        session_model = models.SessionModel(
            user_id=user_id,
            layer_key=state.layer_key,
            projection=state.projection,
            lon=state.lon,
            lat=state.lat,
            zoom=state.zoom,
            date=state.date,
            opacity=state.opacity,
        )
        self.session.add(session_model)
        self.session.commit()
        self.session.refresh(session_model)
        return session_model

    def update_state(self, session_model: models.SessionModel, state: MapState) -> models.SessionModel:
        session_model.layer_key = state.layer_key
        session_model.projection = state.projection
        session_model.lon = state.lon
        session_model.lat = state.lat
        session_model.zoom = state.zoom
        session_model.date = state.date
        session_model.opacity = state.opacity

        self.session.add(session_model)
        self.session.commit()
        self.session.refresh(session_model)
        return session_model
