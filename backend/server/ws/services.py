from typing import Optional

from ..services import *
from ..pd_model import *
from ..settings import REQUEST_TYPES

__all__ = ["user_request"]


def user_request(ws_id: Optional[str], data: Optional[StandardModel]) \
        -> Optional[StandardModel]:
    response = StandardModel(type=data.type, data={})
    try:
        assert data.type in REQUEST_TYPES

        if data.type == "fetchPreview":
            response.data = preview_processing(PreviewData(**data.data))
        elif data.type == "getVectors":
            vector_processing(ws_id, VectorsRequest(**data.data))

        elif data.type == "refuseVectors":
            refuse_processing(ws_id)

    except AttributeError:
        response.data["status"] = False
        response.data["message"] = "Type is not corrected"
    else:
        if response.data == {}:
            response.data["status"] = True
            response.data["message"] = "Processing"
    return response