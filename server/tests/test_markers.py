import http

import pytest

from app.models import MAX_IMPORT_SIZE

VALID = {"lng": 34.78, "lat": 32.07, "score": 3}


@pytest.fixture(autouse=True)
def never_fail(monkeypatch):
    """Make creation deterministic for the API tests; failure tests override this."""
    monkeypatch.setattr("app.failure.should_fail", lambda: False)


def test_list_empty(client):
    """Verify that listing markers returns empty list when no markers exist."""
    assert client.get("/markers").json() == {"markers": []}


def test_export_is_a_json_download(client, marker):
    """Verify that GET /markers/export returns the marker list as an attachment."""
    response = client.get("/markers/export")

    assert response.status_code == http.HTTPStatus.OK
    assert response.headers["content-disposition"] == 'attachment; filename="markers.json"'
    assert response.json() == {"markers": [marker]}


def test_create_returns_marker_with_id(client):
    """Verify that POST creates a marker with a generated id and stores it."""
    response = client.post("/markers", json=VALID)

    assert response.status_code == http.HTTPStatus.CREATED
    body = response.json()
    assert body["id"]
    assert {k: body[k] for k in VALID} == VALID
    assert client.get("/markers").json()["markers"] == [body]


def test_create_fails_when_injected(client, monkeypatch):
    """Verify that POST returns 503 when failure is injected and marker is not created."""
    monkeypatch.setattr("app.failure.should_fail", lambda: True)

    response = client.post("/markers", json=VALID)

    assert response.status_code == http.HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {"detail": "Server refused to create marker"}
    assert client.get("/markers").json() == {"markers": []}


@pytest.mark.parametrize(
    "bad",
    [
        {**VALID, "lng": 181},
        {**VALID, "lat": -91},
        {**VALID, "score": 6},
        {**VALID, "score": -1},
        {**VALID, "score": 2.5},
        {"lng": 1, "lat": 2},
    ],
)
def test_create_rejects_invalid(client, bad):
    """Verify that POST returns 422 for invalid marker data and does not create it."""
    assert client.post("/markers", json=bad).status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY
    assert client.get("/markers").json() == {"markers": []}


def test_replace_updates_marker(client, marker):
    """Verify that PUT replaces an existing marker with new data."""
    new = {"lng": 1.0, "lat": 2.0, "score": 5}

    response = client.put(f"/markers/{marker['id']}", json=new)

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {**new, "id": marker["id"]}
    assert client.get("/markers").json()["markers"] == [response.json()]


def test_replace_unknown_is_404(client):
    """Verify that PUT on an unknown id returns 404."""
    response = client.put("/markers/nope", json=VALID)

    assert response.status_code == http.HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Marker not found"}


def test_delete_removes_marker(client, marker):
    """Verify that DELETE removes an existing marker."""
    assert client.delete(f"/markers/{marker['id']}").status_code == http.HTTPStatus.NO_CONTENT
    assert client.get("/markers").json() == {"markers": []}


def test_delete_unknown_is_404(client):
    """Verify that DELETE on an unknown id returns 404."""
    assert client.delete("/markers/nope").status_code == http.HTTPStatus.NOT_FOUND


def test_import_appends_with_new_ids(client, marker):
    """Verify that POST /import creates markers with generated ids and appends to store."""
    payload = {"markers": [{**VALID, "score": 0}, {**VALID, "score": 5}]}

    response = client.post("/markers/import", json=payload)

    assert response.status_code == http.HTTPStatus.CREATED
    imported = response.json()["markers"]
    assert [m["score"] for m in imported] == [0, 5]
    assert all(m["id"] for m in imported)
    assert len(client.get("/markers").json()["markers"]) == 3


def test_import_is_atomic_on_invalid_item(client):
    """Verify that POST /import rejects the entire batch if any item is invalid."""
    payload = {"markers": [VALID, {**VALID, "score": 9}]}

    response = client.post("/markers/import", json=payload)
    assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY
    assert client.get("/markers").json() == {"markers": []}


def test_import_rejects_oversized_batch(client):
    """Verify that POST /import refuses more than MAX_IMPORT_SIZE markers."""
    payload = {"markers": [VALID] * (MAX_IMPORT_SIZE + 1)}

    response = client.post("/markers/import", json=payload)

    assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY
    assert client.get("/markers").json() == {"markers": []}


def test_import_never_fails_randomly(client, monkeypatch):
    """Verify that POST /import succeeds even when failure is injected."""
    monkeypatch.setattr("app.failure.should_fail", lambda: True)

    response = client.post("/markers/import", json={"markers": [VALID]})
    assert response.status_code == http.HTTPStatus.CREATED


def test_delete_all(client, marker):
    """Verify that DELETE /markers removes all markers."""
    assert client.delete("/markers").status_code == http.HTTPStatus.NO_CONTENT
    assert client.get("/markers").json() == {"markers": []}
