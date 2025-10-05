from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from sqlalchemy.orm import Session

from app.repositories.layers import LayerRepository
from app.schemas import Layer


class LayerService:
    def __init__(self, db: Session) -> None:
        self.repo = LayerRepository(db)

    def grouped_by_body(self) -> Dict[str, List[Layer]]:
        catalog = defaultdict(list)
        for layer in self.repo.list_all():
            catalog[layer.body].append(layer)
        return dict(catalog)
