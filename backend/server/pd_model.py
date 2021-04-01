from pydantic import BaseModel

__all__ = ["StandardModel", "ProcessingData"]


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
