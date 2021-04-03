from typing import List
from pydantic import BaseModel

__all__ = ["StandardModel", "PreviewRequest", "PreviewData", "VectorsRequest", "VectorResult"]


class StandardModel(BaseModel):
    type: str
    data: dict

    class Config:
        arbitrary_types_allowed = True


class Point(BaseModel):
    lon: float
    lat: float

    class Config:
        arbitrary_types_allowed = True


class PreviewRequest(BaseModel):
    datetime: int
    bbox: List[Point]

    class Config:
        arbitrary_types_allowed = True


class PreviewData(BaseModel):
    img: str
    datetime: int
    bbox: List[Point]

    class Config:
        arbitrary_types_allowed = True


class VectorsRequest(BaseModel):
    ids: List[str]
    points: List[Point]
    window_size: int
    vicinity_size: int

    class Config:
        arbitrary_types_allowed = True


class VectorResult(BaseModel):
    ws_id: str
    vector = List[List[float]]
    velocity: float
    error: str

    class Config:
        arbitrary_types_allowed = True
