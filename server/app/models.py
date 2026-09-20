from pydantic import BaseModel, Field


class MarkerIn(BaseModel):
    """What the client sends when creating or replacing a marker."""

    lng: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-90, le=90)
    score: int = Field(ge=0, le=5)


class Marker(MarkerIn):
    """Stored marker: same fields plus the server-generated id."""

    id: str


MAX_IMPORT_SIZE = 1000


class MarkersImport(BaseModel):
    markers: list[MarkerIn] = Field(max_length=MAX_IMPORT_SIZE)


class MarkersOut(BaseModel):
    markers: list[Marker]
