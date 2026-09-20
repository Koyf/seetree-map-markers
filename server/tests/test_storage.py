from pathlib import Path

from app.models import MarkerIn
from app.storage import MarkerStore

VALID = MarkerIn(lng=34.78, lat=32.07, score=3)


def test_markers_survive_a_restart(tmp_path: Path):
    """Verify that a store reopened on the same file sees what the previous one saved."""
    path = tmp_path / "markers.json"
    first = MarkerStore(path)
    kept = first.add(VALID)
    first.add(VALID)
    first.remove(kept.id)
    first.replace(first.all()[0].id, MarkerIn(lng=1, lat=2, score=5))

    second = MarkerStore(path)

    assert second.all() == first.all()
    assert second.all()[0].score == 5


def test_add_many_writes_once_and_keeps_existing(tmp_path: Path):
    """Verify that add_many appends to what is already in the file."""
    store = MarkerStore(tmp_path / "markers.json")
    store.add(VALID)

    added = store.add_many([VALID, VALID])

    assert len(added) == 2
    assert len(store.all()) == 3


def test_clear_empties_the_file(tmp_path: Path):
    """Verify that clear() persists an empty list."""
    path = tmp_path / "markers.json"
    store = MarkerStore(path)
    store.add(VALID)
    store.clear()

    assert MarkerStore(path).all() == []


def test_missing_file_starts_empty(tmp_path: Path):
    """Verify that a store on a file that does not exist yet starts with no markers."""
    assert MarkerStore(tmp_path / "missing.json").all() == []
