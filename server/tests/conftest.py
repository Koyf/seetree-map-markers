import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import store


@pytest.fixture(autouse=True)
def clean_store():
    """Clear the store before and after each test."""
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client():
    """A test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def marker(client):
    """A marker that already exists on the server."""
    return client.post("/markers", json={"lng": 34.78, "lat": 32.07, "score": 3}).json()
