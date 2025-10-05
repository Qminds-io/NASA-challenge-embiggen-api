"""create base tables

Revision ID: d5f4b1acb11e
Revises: 
Create Date: 2025-10-05 11:21:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "d5f4b1acb11e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "layers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("layer_key", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=50), nullable=False),
        sa.Column("body", sa.String(length=50), nullable=False),
        sa.Column("projection", sa.String(length=64), nullable=False),
        sa.Column("matrix_set", sa.String(length=128), nullable=True),
        sa.Column("image_format", sa.String(length=16), nullable=True),
        sa.Column("style", sa.String(length=64), nullable=True),
        sa.Column("max_zoom", sa.Integer(), nullable=True),
        sa.Column("default_date", sa.Date(), nullable=True),
        sa.Column("source_template", sa.String(length=1024), nullable=False),
        sa.UniqueConstraint("layer_key", name="uq_layers_layer_key"),
    )
    op.create_index("ix_layers_layer_key", "layers", ["layer_key"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("api_token_hash", sa.String(length=128), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

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
        sa.Column(
            "properties",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("annotations")
    op.drop_table("users")
    op.drop_index("ix_layers_layer_key", table_name="layers")
    op.drop_table("layers")
