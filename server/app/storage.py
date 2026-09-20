import json
import os
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.models import Marker, MarkerIn, MarkersOut


class MarkerStore:
    """Markers live in one JSON file; every operation reads and writes it under a lock."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = Lock()

    def all(self) -> list[Marker]:
        """List all markers."""
        with self._lock:
            return list(self._read().values())

    def add(self, data: MarkerIn) -> Marker:
        """Add a new marker and return it."""
        marker = Marker(id=str(uuid4()), **data.model_dump())
        with self._lock:
            markers = self._read()
            markers[marker.id] = marker
            self._write(markers)
        return marker

    def add_many(self, items: list[MarkerIn]) -> list[Marker]:
        """Add several markers in one write and return them."""
        added = [Marker(id=str(uuid4()), **item.model_dump()) for item in items]
        with self._lock:
            markers = self._read()
            markers.update({m.id: m for m in added})
            self._write(markers)
        return added

    def replace(self, marker_id: str, data: MarkerIn) -> Marker | None:
        """Replace an existing marker and return it, or None if not found."""
        marker = Marker(id=marker_id, **data.model_dump())
        with self._lock:
            markers = self._read()
            if marker_id not in markers:
                return None
            markers[marker_id] = marker
            self._write(markers)
        return marker

    def remove(self, marker_id: str) -> bool:
        """Remove a marker by id. Return True if it was removed, False if not found."""
        with self._lock:
            markers = self._read()
            if markers.pop(marker_id, None) is None:
                return False
            self._write(markers)
        return True

    def clear(self) -> None:
        """Remove all markers."""
        with self._lock:
            self._write({})

    def _read(self) -> dict[str, Marker]:
        """Load the file into a dict by id; a missing file means no markers."""
        if not self._path.exists():
            return {}
        markers = MarkersOut.model_validate_json(self._path.read_text()).markers
        return {m.id: m for m in markers}

    def _write(self, markers: dict[str, Marker]) -> None:
        """Write the whole file atomically via a temp file."""
        payload = MarkersOut(markers=list(markers.values())).model_dump()
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload))
        tmp.replace(self._path)


store = MarkerStore(Path(os.getenv("MARKERS_FILE", "data/markers.json")))
