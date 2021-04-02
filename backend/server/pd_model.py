from pydantic import BaseModel

__all__ = ["StandardModel", "PreviewRequest", "PreviewData", "VectorsRequest", "VectorResult"]


class StandardModel(BaseModel):
    type: str
    data: dict


class Point(BaseModel):
    lon: float
    lat: float


class PreviewRequest(BaseModel):
    datetime: int
    bbox: list[Point, Point]


class PreviewData(BaseModel):
    img: str
    datetime: int
    bbox: list[Point, Point]


class VectorsRequest(BaseModel):
    ids: list[str, str]
    points: list[Point]
    window_size: int
    vicinity_size: int


class VectorResult(BaseModel):
    ws_id: str
    vector = list[Point, Point]
    velocity: float
    error: str
