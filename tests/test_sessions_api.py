from __future__ import annotations

from datetime import date as DateType

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.db import models
from app.repositories.layers import LayerRepository, default_layers


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

    with TestingSessionLocal() as session:
        LayerRepository(session).ensure_seeded(default_layers())

    origin_header = settings.allowed_origins[0]
    headers = {"Origin": origin_header}

    with TestClient(app) as client:
        yield client, headers

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_list_layers_returns_grouped_catalog(api_client):
    client, headers = api_client
    response = client.get("/v1/layers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "earth" in data
    assert any(layer["layerKey"].startswith("gibs:") for layer in data["earth"])


def test_sessions_crud_flow(api_client):
    client, headers = api_client

    session_payload = {
        "state": {
            "lon": -58.45,
            "lat": -34.6,
            "zoom": 4,
            "date": DateType(2024, 1, 5).isoformat(),
            "layerKey": "gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
            "projection": "EPSG:3857",
            "opacity": 0.75,
        },
        "annotations": [],
    }

    create_response = client.post("/v1/sessions", json=session_payload, headers=headers)
    assert create_response.status_code == 201
    created = create_response.json()
    session_id = created["id"]
    assert created["state"]["layerKey"] == session_payload["state"]["layerKey"]

    list_response = client.get("/v1/sessions", headers=headers)
    assert list_response.status_code == 200
    sessions = list_response.json()
    assert len(sessions) == 1

    update_payload = {
        "state": {
            **session_payload["state"],
            "zoom": 5,
        },
        "annotations": [
            {
                "feature": {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-58.45, -34.6]},
                    "properties": {"name": "Buenos Aires"},
                },
                "order": 0,
                "properties": {"color": "#FF0000"},
            }
        ],
    }

    update_response = client.put(f"/v1/sessions/{session_id}", json=update_payload, headers=headers)
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["state"]["zoom"] == 5
    assert len(updated["annotations"]) == 1

    annotations_payload = {
        "features": [
            {
                "feature": {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-58.5, -34.61]},
                    "properties": {"name": "Marker"},
                },
                "order": 1,
                "properties": {"color": "#00FF00"},
            }
        ],
    }

    annotations_response = client.post(
        f"/v1/sessions/{session_id}/annotations",
        json=annotations_payload,
        headers=headers,
    )
    assert annotations_response.status_code == 200
    feature_collection = annotations_response.json()
    assert feature_collection["type"] == "FeatureCollection"
    assert len(feature_collection["features"]) == 1


def test_sessions_require_origin_header(api_client):
    client, headers = api_client
    response = client.get("/v1/sessions")
    assert response.status_code == 403
