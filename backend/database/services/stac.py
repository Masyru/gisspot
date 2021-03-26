from datetime import datetime, timedelta
from pystac import Item

from .pro_files import b0_proj_dt


def create_item(i_id: str, metadata: b0_proj_dt) -> Item:
    geometry: dict = {}
    bbox: list[float] = [
        metadata["b0_proj_common"]["lon"][0],
        metadata["b0_proj_common"]["lat"][0],
        metadata["b0_proj_common"]["lonSize"][0],
        metadata["b0_proj_common"]["latSize"][0],
    ]
    datetime_item: datetime = datetime(year=metadata["b0_common"]["year"][0], month=1, day=1)
    datetime_item += timedelta(days=int(metadata["b0_common"]["day"][0]),
                               milliseconds=int(metadata["b0_common"]["dayTime"][0]))
    properties: dict = {}
    return Item(id=i_id,
                geometry=geometry,
                bbox=bbox,
                datetime=datetime_item,
                properties=properties)
