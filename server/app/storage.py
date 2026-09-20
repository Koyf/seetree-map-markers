from threading import Lock
from uuid import uuid4

from app.models import Marker, MarkerIn


class MarkerStore:
    """In-memory marker storage. One instance lives for the whole process."""

    def __init__(self) -> None:
        self._markers: dict[str, Marker] = {}
        self._lock = Lock()

    def all(self) -> list[Marker]:
        """List all markers."""
        with self._lock:
            return list(self._markers.values())

    def add(self, data: MarkerIn) -> Marker:
        """Add a new marker and return it."""
        marker = Marker(id=str(uuid4()), **data.model_dump())
        with self._lock:
            self._markers[marker.id] = marker
        return marker

    def replace(self, marker_id: str, data: MarkerIn) -> Marker | None:
        """Replace an existing marker and return it, or None if not found."""
        marker = Marker(id=marker_id, **data.model_dump())
        with self._lock:
            if marker_id not in self._markers:
                return None
            self._markers[marker_id] = marker
        return marker

    def remove(self, marker_id: str) -> bool:
        """Remove a marker by id. Return True if it was removed, False if not found."""
        with self._lock:
            return self._markers.pop(marker_id, None) is not None

    def clear(self) -> None:
        """Remove all markers."""
        with self._lock:
            self._markers.clear()


store = MarkerStore()
