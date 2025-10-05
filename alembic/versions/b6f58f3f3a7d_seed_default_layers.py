"""seed default layers

Revision ID: b6f58f3f3a7d
Revises: a8a5b7e07f81
Create Date: 2025-10-05 12:50:00

"""
from __future__ import annotations

from datetime import date

from alembic import op
import sqlalchemy as sa


revision = "b6f58f3f3a7d"
down_revision = "a8a5b7e07f81"
branch_labels = None
depends_on = None

_LAYER_KEYS = (
    "gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
    "trek:Moon:LRO_LOLA_ClrShade_Global_128ppd_v04",
    "trek:Mars:CTX_Mosaic_Global_6ppd",
)


def upgrade() -> None:
    layers_table = sa.table(
        "layers",
        sa.column("layer_key", sa.String(length=255)),
        sa.column("title", sa.String(length=255)),
        sa.column("kind", sa.String(length=50)),
        sa.column("body", sa.String(length=50)),
        sa.column("projection", sa.String(length=64)),
        sa.column("matrix_set", sa.String(length=128)),
        sa.column("image_format", sa.String(length=16)),
        sa.column("style", sa.String(length=64)),
        sa.column("max_zoom", sa.Integer()),
        sa.column("default_date", sa.Date()),
        sa.column("source_template", sa.String(length=1024)),
    )

    op.bulk_insert(
        layers_table,
        [
            {
                "layer_key": "gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
                "title": "MODIS Terra True Color",
                "kind": "gibs",
                "body": "earth",
                "projection": "EPSG:3857",
                "matrix_set": "GoogleMapsCompatible_Level9",
                "image_format": "jpg",
                "style": "default",
                "max_zoom": 9,
                "default_date": date(2024, 1, 1),
                "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
            },
            {
                "layer_key": "trek:Moon:LRO_LOLA_ClrShade_Global_128ppd_v04",
                "title": "LRO LOLA Color Shaded Relief",
                "kind": "trek",
                "body": "moon",
                "projection": "EPSG:4326",
                "matrix_set": "default028mm",
                "image_format": "png",
                "style": "default",
                "max_zoom": 8,
                "default_date": None,
                "source_template": "{body}/EQ/{layer}/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
            },
            {
                "layer_key": "trek:Mars:CTX_Mosaic_Global_6ppd",
                "title": "CTX Global Mosaic",
                "kind": "trek",
                "body": "mars",
                "projection": "EPSG:4326",
                "matrix_set": "default028mm",
                "image_format": "png",
                "style": "default",
                "max_zoom": 9,
                "default_date": None,
                "source_template": "{body}/EQ/{layer}/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
            },
        ],
    )


def downgrade() -> None:
    layers_table = sa.table(
        "layers",
        sa.column("layer_key", sa.String(length=255)),
    )
    op.execute(
        sa.delete(layers_table).where(layers_table.c.layer_key.in_(_LAYER_KEYS))
    )