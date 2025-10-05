from __future__ import annotations

from dataclasses import dataclass
from datetime import date as DateType
from typing import Dict, Optional


@dataclass(frozen=True)
class LayerConfig:
    layer_key: str
    title: str
    kind: str
    body: str
    projection: str
    matrix_set: Optional[str]
    image_format: Optional[str]
    style: Optional[str]
    max_zoom: Optional[int]
    default_date: Optional[DateType]
    source_template: str


_LAYERS: tuple[LayerConfig, ...] = (
    LayerConfig(
        layer_key="gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
        title="MODIS Terra True Color",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level9",
        image_format="jpg",
        style="default",
        max_zoom=9,
        default_date=DateType(2024, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="gibs:MODIS_Aqua_CorrectedReflectance_TrueColor",
        title="MODIS Aqua True Color",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level9",
        image_format="jpg",
        style="default",
        max_zoom=9,
        default_date=DateType(2024, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="gibs:VIIRS_SNPP_CorrectedReflectance_TrueColor",
        title="VIIRS SNPP True Color",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level9",
        image_format="jpg",
        style="default",
        max_zoom=9,
        default_date=DateType(2024, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="gibs:MODIS_Terra_CorrectedReflectance_Bands721",
        title="MODIS Terra Bands 7-2-1",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level9",
        image_format="jpg",
        style="default",
        max_zoom=9,
        default_date=DateType(2024, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="gibs:MODIS_Terra_CorrectedReflectance_Bands367",
        title="MODIS Terra Bands 3-6-7",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level9",
        image_format="jpg",
        style="default",
        max_zoom=9,
        default_date=DateType(2024, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="gibs:BlueMarble_ShadedRelief",
        title="Blue Marble Shaded Relief",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level8",
        image_format="jpg",
        style="default",
        max_zoom=8,
        default_date=DateType(2004, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="gibs:BlueMarble_ShadedRelief_Bathymetry",
        title="Blue Marble Relief Bathymetry",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level8",
        image_format="jpg",
        style="default",
        max_zoom=8,
        default_date=DateType(2004, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="gibs:VIIRS_CityLights_2012",
        title="VIIRS City Lights 2012",
        kind="gibs",
        body="Earth",
        projection="EPSG:3857",
        matrix_set="GoogleMapsCompatible_Level8",
        image_format="jpg",
        style="default",
        max_zoom=8,
        default_date=DateType(2012, 1, 1),
        source_template="{layerId}/default/{date}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="trek:Mars:Mars_MGS_MOLA_ClrShade_merge_global_463m",
        title="Mars MOLA Color Shaded",
        kind="trek",
        body="Mars",
        projection="EPSG:4326",
        matrix_set="default028mm",
        image_format="jpg",
        style="default",
        max_zoom=10,
        default_date=None,
        source_template="https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="trek:Mars:Mars_Viking_MDIM21_ClrMosaic_global_232m",
        title="Mars Viking MDIM21 Color Mosaic",
        kind="trek",
        body="Mars",
        projection="EPSG:4326",
        matrix_set="default028mm",
        image_format="jpg",
        style="default",
        max_zoom=10,
        default_date=None,
        source_template="https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="trek:Moon:LRO_LOLA_ClrShade_Global_128ppd_v04",
        title="Moon LRO LOLA Color Shaded",
        kind="trek",
        body="Moon",
        projection="EPSG:4326",
        matrix_set="default028mm",
        image_format="png",
        style="default",
        max_zoom=8,
        default_date=None,
        source_template="https://trek.nasa.gov/tiles/Moon/EQ/LRO_LOLA_ClrShade_Global_128ppd_v04/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
    LayerConfig(
        layer_key="trek:Ceres:Ceres_Dawn_FC_HAMO_ClrShade_DLR_Global_60ppd_Oct2016",
        title="Ceres Dawn FC HAMO Color Shaded",
        kind="trek",
        body="Ceres",
        projection="EPSG:4326",
        matrix_set="default028mm",
        image_format="jpg",
        style="default",
        max_zoom=10,
        default_date=None,
        source_template="https://trek.nasa.gov/tiles/Ceres/EQ/Ceres_Dawn_FC_HAMO_ClrShade_DLR_Global_60ppd_Oct2016/1.0.0/{style}/{matrixSet}/{z}/{y}/{x}.{format}",
    ),
)

_LAYER_BY_KEY: Dict[str, LayerConfig] = {layer.layer_key: layer for layer in _LAYERS}


def get_layer(layer_key: str) -> Optional[LayerConfig]:
    return _LAYER_BY_KEY.get(layer_key)


def all_layers() -> Dict[str, LayerConfig]:
    return dict(_LAYER_BY_KEY)