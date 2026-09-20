import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import MarkerStore


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch, tmp_path):
    """Point the routes at an empty store in a temporary file."""
    monkeypatch.setattr("app.routes.store", MarkerStore(tmp_path / "markers.json"))


@pytest.fixture
def client():
    """A test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def marker(client):
    """A marker that already exists on the server."""
    return client.post("/markers", json={"lng": 34.78, "lat": 32.07, "score": 3}).json()
