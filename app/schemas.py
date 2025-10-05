from __future__ import annotations

from datetime import date as DateType, datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


LayerKind = Literal["gibs", "trek"]


class Layer(CamelModel):
    layer_key: str = Field(..., description="Identificador unico de la capa.")
    title: str = Field(..., description="Nombre legible para el visor.")
    kind: LayerKind = Field(..., description="Proveedor de la capa (gibs o trek).")
    body: str = Field(..., description="Cuerpo celeste asociado.")
    projection: str = Field(..., description="Proyeccion utilizada.")
    matrix_set: Optional[str] = Field(default=None, description="Tile matrix set NASA.")
    image_format: Optional[str] = Field(default=None, description="Formato del tile.")
    tile_template: str = Field(..., description="Template interno para tiles proxied.")
    max_zoom: Optional[int] = Field(default=None, description="Zoom maximo soportado.")
    default_date: Optional[DateType] = Field(
        default=None, description="Fecha por defecto para capas temporales."
    )


class MapState(CamelModel):
    lon: float = Field(..., description="Longitud del centro.")
    lat: float = Field(..., description="Latitud del centro.")
    zoom: int = Field(..., ge=0, description="Nivel de zoom.")
    date: Optional[DateType] = Field(
        default=None, description="Fecha activa para capas temporales."
    )
    layer_key: str = Field(..., description="Capa visible actualmente.")
    projection: str = Field(..., description="Proyeccion del mapa.")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Opacidad (0-1).")


class Annotation(CamelModel):
    id: Optional[int] = Field(default=None)
    session_id: Optional[int] = Field(default=None)
    feature: Dict[str, Any] = Field(..., description="GeoJSON Feature completo.")
    order: int = Field(default=0, ge=0)
    properties: Dict[str, Any] = Field(default_factory=dict)


class Session(CamelModel):
    id: int
    state: MapState
    annotations: List[Annotation] = Field(default_factory=list)
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class User(CamelModel):
    id: Optional[int] = None
    username: str
    api_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionCreateRequest(CamelModel):
    state: MapState
    annotations: List[Annotation] = Field(default_factory=list)


class SessionUpdateRequest(CamelModel):
    state: MapState
    annotations: Optional[List[Annotation]] = None


class AnnotationUpsertRequest(CamelModel):
    features: List[Annotation] = Field(default_factory=list)
