"""update annotations schema

Revision ID: a8a5b7e07f81
Revises: d5f4b1acb11e
Create Date: 2025-10-05 12:46:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "a8a5b7e07f81"
down_revision = "d5f4b1acb11e"
branch_labels = None
depends_on = None


EXPECTED_COLUMNS = {
    "id",
    "external_id",
    "title",
    "description",
    "order",
    "feature",
    "lat",
    "lon",
    "layer_key",
    "date",
    "projection",
    "zoom",
    "opacity",
    "center_lat",
    "center_lon",
    "extent_min_lat",
    "extent_min_lon",
    "extent_max_lat",
    "extent_max_lon",
    "properties",
    "created_at",
    "updated_at",
}


def _annotations_is_up_to_date(bind) -> bool:
    inspector = inspect(bind)
    if "annotations" not in inspector.get_table_names():
        return False
    existing_columns = {col["name"] for col in inspector.get_columns("annotations")}
    return EXPECTED_COLUMNS.issubset(existing_columns)


def upgrade() -> None:
    bind = op.get_bind()
    if _annotations_is_up_to_date(bind):
        return

    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "annotations" in tables:
        op.drop_table("annotations")
    if "sessions" in tables:
        op.drop_table("sessions")

    op.create_table(
        "annotations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("feature", sa.JSON(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("layer_key", sa.String(length=255), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("projection", sa.String(length=64), nullable=True),
        sa.Column("zoom", sa.Float(), nullable=True),
        sa.Column("opacity", sa.Float(), nullable=True),
        sa.Column("center_lat", sa.Float(), nullable=True),
        sa.Column("center_lon", sa.Float(), nullable=True),
        sa.Column("extent_min_lat", sa.Float(), nullable=True),
        sa.Column("extent_min_lon", sa.Float(), nullable=True),
        sa.Column("extent_max_lat", sa.Float(), nullable=True),
        sa.Column("extent_max_lon", sa.Float(), nullable=True),
        sa.Column("properties", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("annotations")

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("layer_key", sa.String(length=255), nullable=False),
        sa.Column("projection", sa.String(length=64), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("zoom", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("opacity", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
    )

    op.create_table(
        "annotations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("feature", sa.JSON(), nullable=False),
        sa.Column("properties", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], name="fk_annotations_session_id_sessions", ondelete="CASCADE"),
    )
