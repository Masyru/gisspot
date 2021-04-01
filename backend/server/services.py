from typing import Optional

from backend.server.pd_model import *
from backend.server.settings import REQUEST_TYPES

__all__ = ["main_processing"]


def main_processing(data: Optional[StandardModel]) \
        -> Optional[StandardModel]:
    assert data.type in REQUEST_TYPES
    return data
