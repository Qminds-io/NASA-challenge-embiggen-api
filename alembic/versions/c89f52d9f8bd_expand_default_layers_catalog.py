"""expand default layers catalog"""

from __future__ import annotations

from datetime import date

from alembic import op
import sqlalchemy as sa


revision = "c89f52d9f8bd"
down_revision = "b6f58f3f3a7d"
branch_labels = None
depends_on = None

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

OLD_KEYS = {
    "gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
    "trek:Moon:LRO_LOLA_ClrShade_Global_128ppd_v04",
    "trek:Mars:CTX_Mosaic_Global_6ppd",
}

NEW_LAYERS = [
    {
        "layer_key": "gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
        "title": "MODIS Terra True Color",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level9",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 9,
        "default_date": date(2024, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "gibs:MODIS_Aqua_CorrectedReflectance_TrueColor",
        "title": "MODIS Aqua True Color",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level9",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 9,
        "default_date": date(2024, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "gibs:VIIRS_SNPP_CorrectedReflectance_TrueColor",
        "title": "VIIRS SNPP True Color",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level9",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 9,
        "default_date": date(2024, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "gibs:MODIS_Terra_CorrectedReflectance_Bands721",
        "title": "MODIS Terra Bands 7-2-1",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level9",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 9,
        "default_date": date(2024, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "gibs:MODIS_Terra_CorrectedReflectance_Bands367",
        "title": "MODIS Terra Bands 3-6-7",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level9",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 9,
        "default_date": date(2024, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "gibs:BlueMarble_ShadedRelief",
        "title": "Blue Marble Shaded Relief",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level8",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 8,
        "default_date": date(2004, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "gibs:BlueMarble_ShadedRelief_Bathymetry",
        "title": "Blue Marble Relief Bathymetry",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level8",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 8,
        "default_date": date(2004, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "gibs:VIIRS_CityLights_2012",
        "title": "VIIRS City Lights 2012",
        "kind": "gibs",
        "body": "Earth",
        "projection": "EPSG:3857",
        "matrix_set": "GoogleMapsCompatible_Level8",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 8,
        "default_date": date(2012, 1, 1),
        "source_template": "{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "trek:Mars:Mars_MGS_MOLA_ClrShade_merge_global_463m",
        "title": "Mars MOLA Color Shaded",
        "kind": "trek",
        "body": "Mars",
        "projection": "EPSG:4326",
        "matrix_set": "default028mm",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 10,
        "default_date": None,
        "source_template": "https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "trek:Mars:Mars_Viking_MDIM21_ClrMosaic_global_232m",
        "title": "Mars Viking MDIM21 Color Mosaic",
        "kind": "trek",
        "body": "Mars",
        "projection": "EPSG:4326",
        "matrix_set": "default028mm",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 10,
        "default_date": None,
        "source_template": "https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "trek:Moon:LRO_LOLA_ClrShade_Global_128ppd_v04",
        "title": "Moon LRO LOLA Color Shaded",
        "kind": "trek",
        "body": "Moon",
        "projection": "EPSG:4326",
        "matrix_set": "default028mm",
        "image_format": "png",
        "style": "default",
        "max_zoom": 8,
        "default_date": None,
        "source_template": "https://trek.nasa.gov/tiles/Moon/EQ/LRO_LOLA_ClrShade_Global_128ppd_v04/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
    {
        "layer_key": "trek:Ceres:Ceres_Dawn_FC_HAMO_ClrShade_DLR_Global_60ppd_Oct2016",
        "title": "Ceres Dawn FC HAMO Color Shaded",
        "kind": "trek",
        "body": "Ceres",
        "projection": "EPSG:4326",
        "matrix_set": "default028mm",
        "image_format": "jpg",
        "style": "default",
        "max_zoom": 10,
        "default_date": None,
        "source_template": "https://trek.nasa.gov/tiles/Ceres/EQ/Ceres_Dawn_FC_HAMO_ClrShade_DLR_Global_60ppd_Oct2016/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    },
]


def upgrade() -> None:
    op.execute(sa.delete(layers_table).where(layers_table.c.layer_key.in_(OLD_KEYS)))
    op.bulk_insert(layers_table, NEW_LAYERS)


def downgrade() -> None:
    new_keys = {layer["layer_key"] for layer in NEW_LAYERS}
    op.execute(sa.delete(layers_table).where(layers_table.c.layer_key.in_(new_keys)))
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