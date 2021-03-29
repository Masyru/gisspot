from pydantic import BaseModel

__all__ = ["ProcessingData"]


class ProcessingData(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    speed: float
    error_message: str
