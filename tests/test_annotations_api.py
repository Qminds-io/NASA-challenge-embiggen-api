
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db


@pytest.fixture
def api_client(tmp_path):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    import app.main as app_main

    app_main.SessionLocal = TestingSessionLocal  # type: ignore[attr-defined]
    app = app_main.app

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    origin_header = settings.allowed_origins[0]
    headers = {"Origin": origin_header}

    with TestClient(app) as client:
        yield client, headers

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


FRAME_PAYLOAD = {
    "layerKey": "gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
    "date": "2024-05-12",
    "projection": "EPSG:3857",
    "zoom": 4.3,
    "opacity": 0.75,
    "center": {"lon": -58.45, "lat": -34.6},
    "extent": {"minLon": -70.12, "minLat": -42.3, "maxLon": -46.8, "maxLat": -27.1},
}

FEATURE_PAYLOAD = {
    "id": "tmp-123",
    "order": 0,
    "feature": {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-58.45, -34.6]},
        "properties": {"name": "Buenos Aires"},
    },
    "properties": {"color": "#FF0000"},
}


POLYGON_FEATURE_PAYLOAD = {
    "id": "poly-001",
    "order": 1,
    "feature": {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-58.46, -34.59],
                    [-58.44, -34.61],
                    [-58.42, -34.58],
                    [-58.46, -34.59],
                ]
            ],
        },
        "properties": {"name": "Buenos Aires Region"},
    },
    "properties": {"color": "#00FF00"},
}

def test_annotations_crud_and_filter(api_client):
    client, headers = api_client

    create_payload = {
        "frame": FRAME_PAYLOAD,
        "features": [FEATURE_PAYLOAD, POLYGON_FEATURE_PAYLOAD],
    }

    response = client.post("/v1/annotations", json=create_payload, headers=headers)
    assert response.status_code == 201
    created = response.json()
    created_features = created["features"]
    assert len(created_features) == 2
    assert any(
        feature["feature"]["geometry"]["type"] == "Polygon" for feature in created_features
    )
    annotation_ids = [feature["id"] for feature in created_features]

    query_payload = {"frame": FRAME_PAYLOAD, "features": []}
    list_response = client.post("/v1/annotations/query", json=query_payload, headers=headers)
    assert list_response.status_code == 200
    listed_features = list_response.json()["features"]
    assert len(listed_features) == 2

    outside_frame = {
        "frame": {
            **FRAME_PAYLOAD,
            "extent": {"minLon": 0, "minLat": 0, "maxLon": 10, "maxLat": 10},
        },
        "features": [],
    }
    empty_response = client.post("/v1/annotations/query", json=outside_frame, headers=headers)
    assert empty_response.status_code == 200
    assert empty_response.json()["features"] == []

    for annotation_id in annotation_ids:
        delete_response = client.delete(
            f"/v1/annotations/{annotation_id}",
            params={"secret": "qminds"},
            headers=headers,
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "deleted"

    final_response = client.post("/v1/annotations/query", json=query_payload, headers=headers)
    assert final_response.status_code == 200
    assert final_response.json()["features"] == []
