from pydantic import BaseModel

__all__ = ["StandardModel", "ProcessingData", "PreviewRequestData", "PreviewData"]


class StandardModel(BaseModel):
    type: str
    data: dict


class ProcessingData(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    hex: str
    speed: float
    error_message: str


class Point(BaseModel):
    lon: float
    lat: float


class PreviewRequestData(BaseModel):
    datetime: int
    bbox: list[Point, Point]


class PreviewData(BaseModel):
    img: str
    datetime: int
    bbox: list[Point, Point]