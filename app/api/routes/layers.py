from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends

from app.schemas import Layer
from app.dependencies import limit_db_requests
from app.services.layers import LayerService

router = APIRouter(prefix="/v1/layers", tags=["Layers"])


@router.get("", response_model=Dict[str, List[Layer]], summary="Catalogo de capas agrupado por cuerpo celeste")
def list_layers(_: None = Depends(limit_db_requests)) -> Dict[str, List[Layer]]:
    service = LayerService()
    return service.grouped_by_body()