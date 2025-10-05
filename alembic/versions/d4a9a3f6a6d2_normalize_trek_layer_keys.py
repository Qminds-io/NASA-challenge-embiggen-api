"""normalize trek layer keys"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "d4a9a3f6a6d2"
down_revision = "c89f52d9f8bd"
branch_labels = None
depends_on = None

layers = sa.table(
    "layers",
    sa.column("layer_key", sa.String(length=255)),
    sa.column("source_template", sa.String(length=1024)),
)

KEY_UPDATES = {
    "trek:Mars:https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m": (
        "trek:Mars:Mars_MGS_MOLA_ClrShade_merge_global_463m",
        "https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    "trek:Mars:https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m": (
        "trek:Mars:Mars_Viking_MDIM21_ClrMosaic_global_232m",
        "https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    "trek:Moon:https://trek.nasa.gov/tiles/Moon/EQ/LRO_LOLA_ClrShade_Global_128ppd_v04": (
        "trek:Moon:LRO_LOLA_ClrShade_Global_128ppd_v04",
        "https://trek.nasa.gov/tiles/Moon/EQ/LRO_LOLA_ClrShade_Global_128ppd_v04/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    "trek:Ceres:https://trek.nasa.gov/tiles/Ceres/EQ/Ceres_Dawn_FC_HAMO_ClrShade_DLR_Global_60ppd_Oct2016": (
        "trek:Ceres:Ceres_Dawn_FC_HAMO_ClrShade_DLR_Global_60ppd_Oct2016",
        "https://trek.nasa.gov/tiles/Ceres/EQ/Ceres_Dawn_FC_HAMO_ClrShade_DLR_Global_60ppd_Oct2016/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
}


def upgrade() -> None:
    for old_key, (new_key, template) in KEY_UPDATES.items():
        op.execute(
            sa.update(layers)
            .where(layers.c.layer_key == old_key)
            .values(layer_key=new_key, source_template=template)
        )


def downgrade() -> None:
    reverse = {new: (old, template) for old, (new, template) in KEY_UPDATES.items()}
    for new_key, (old_key, template) in reverse.items():
        op.execute(
            sa.update(layers)
            .where(layers.c.layer_key == new_key)
            .values(layer_key=old_key, source_template=template)
        )