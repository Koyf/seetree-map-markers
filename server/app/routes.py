from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app import failure
from app.models import Marker, MarkerIn, MarkersImport, MarkersOut
from app.storage import store

router = APIRouter(prefix="/markers", tags=["markers"])


@router.get("", response_model=MarkersOut)
def list_markers() -> MarkersOut:
    """List all markers."""
    return MarkersOut(markers=store.all())


@router.get("/export")
def export_markers() -> JSONResponse:
    """Same payload as GET /markers, but served as a file download."""
    payload = MarkersOut(markers=store.all()).model_dump()
    return JSONResponse(
        payload, headers={"Content-Disposition": 'attachment; filename="markers.json"'}
    )


@router.post("", response_model=Marker, status_code=status.HTTP_201_CREATED)
def create_marker(data: MarkerIn) -> Marker:
    """Create a new marker."""
    if failure.should_fail():
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="Server refused to create marker"
        )
    return store.add(data)


@router.put("/{marker_id}", response_model=Marker)
def replace_marker(marker_id: str, data: MarkerIn) -> Marker:
    """Replace an existing marker."""
    marker = store.replace(marker_id, data)
    if marker is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Marker not found")
    return marker


@router.delete("/{marker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_marker(marker_id: str) -> None:
    """Delete a marker."""
    if not store.remove(marker_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Marker not found")


@router.post("/import", response_model=MarkersOut, status_code=status.HTTP_201_CREATED)
def import_markers(data: MarkersImport) -> MarkersOut:
    """Import a list of markers."""
    return MarkersOut(markers=[store.add(item) for item in data.markers])


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_markers() -> None:
    """Delete all markers."""
    store.clear()
