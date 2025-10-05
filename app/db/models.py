from __future__ import annotations

from datetime import date as DateType, datetime
from typing import Optional

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LayerModel(Base):
    __tablename__ = "layers"
    __table_args__ = (UniqueConstraint("layer_key", name="uq_layers_layer_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    layer_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    body: Mapped[str] = mapped_column(String(50), nullable=False)
    projection: Mapped[str] = mapped_column(String(64), nullable=False)
    matrix_set: Mapped[Optional[str]] = mapped_column(String(128))
    image_format: Mapped[Optional[str]] = mapped_column(String(16))
    style: Mapped[Optional[str]] = mapped_column(String(64))
    max_zoom: Mapped[Optional[int]] = mapped_column(Integer)
    default_date: Mapped[Optional[DateType]] = mapped_column(Date)
    source_template: Mapped[str] = mapped_column(String(1024), nullable=False)


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="uq_users_username"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    api_token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    sessions: Mapped[list["SessionModel"]] = relationship(
        "SessionModel", back_populates="user", cascade="all, delete-orphan"
    )


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    layer_key: Mapped[str] = mapped_column(String(255), nullable=False)
    projection: Mapped[str] = mapped_column(String(64), nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    zoom: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[Optional[DateType]] = mapped_column(Date)
    opacity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="sessions")
    annotations: Mapped[list["AnnotationModel"]] = relationship(
        "AnnotationModel", back_populates="session", cascade="all, delete-orphan"
    )


class AnnotationModel(Base):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    feature: Mapped[dict] = mapped_column(JSON, nullable=False)
    properties: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    session: Mapped["SessionModel"] = relationship(
        "SessionModel", back_populates="annotations"
    )
