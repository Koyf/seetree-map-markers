import json
import os
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.models import Marker, MarkerIn, MarkersOut


class MarkerStore:
    """Markers in memory, mirrored to a JSON file when a path is given."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._lock = Lock()
        self._markers: dict[str, Marker] = {m.id: m for m in self._load()}

    def all(self) -> list[Marker]:
        with self._lock:
            return list(self._markers.values())

    def add(self, data: MarkerIn) -> Marker:
        marker = Marker(id=str(uuid4()), **data.model_dump())
        with self._lock:
            self._markers[marker.id] = marker
            self._save()
        return marker

    def replace(self, marker_id: str, data: MarkerIn) -> Marker | None:
        marker = Marker(id=marker_id, **data.model_dump())
        with self._lock:
            if marker_id not in self._markers:
                return None
            self._markers[marker_id] = marker
            self._save()
        return marker

    def remove(self, marker_id: str) -> bool:
        with self._lock:
            removed = self._markers.pop(marker_id, None) is not None
            if removed:
                self._save()
        return removed

    def clear(self) -> None:
        with self._lock:
            self._markers.clear()
            self._save()

    def _load(self) -> list[Marker]:
        if self._path is None or not self._path.exists():
            return []
        return MarkersOut.model_validate_json(self._path.read_text()).markers

    def _save(self) -> None:
        if self._path is None:
            return
        payload = MarkersOut(markers=list(self._markers.values())).model_dump()
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload))
        os.replace(tmp, self._path)


def _path_from_env() -> Path | None:
    value = os.getenv("MARKERS_FILE")
    return Path(value) if value else None


store = MarkerStore(_path_from_env())
