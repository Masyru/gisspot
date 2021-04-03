from datetime import datetime, timedelta
from pystac import Asset, Catalog, Collection, Item
from typing import Union, Optional, List
from os import path

import sys
sys.path.append("../../../")
from backend.database.services.pro_files import b0_proj_dt

__all__ = ["add_assets", "create_item", "normalize_stac_path", "filter_catalog", "path_gen"]


def create_item(i_id: str,
                metadata: b0_proj_dt) \
        -> Item:
    geometry: dict = {}
    bbox: list[float] = [
        float(metadata["b0_proj_common"]["lon"][0]),
        float(metadata["b0_proj_common"]["lat"][0]),
        float(metadata["b0_proj_common"]["lonSize"][0]),
        float(metadata["b0_proj_common"]["latSize"][0]),
    ]
    bbox[2] += bbox[0]  # Конечные координаты = Размер + начальные координаты
    bbox[3] += bbox[1]
    datetime_item: datetime = datetime(year=metadata["b0_common"]["year"][0], month=1, day=1)
    datetime_item += timedelta(days=int(metadata["b0_common"]["day"][0]),
                               milliseconds=int(metadata["b0_common"]["dayTime"][0]))
    properties: dict = {}
    return Item(id=i_id,
                geometry=geometry,
                bbox=bbox,
                datetime=datetime_item,
                properties=properties)


def add_assets(item: Optional[Item],
               assets: List[Asset]) \
        -> None:
    assets_count = len(item.get_assets())

    for asset in assets:
        item.add_asset(str(assets_count), asset=asset)
        assets_count += 1


def normalize_stac_path(stac_path: Optional[str]) -> str:
    if not stac_path.endswith("catalog.json"):
        stac_path = path.join(stac_path, "catalog.json")

    if not stac_path.startswith("http") and \
            not stac_path.startswith("file"):
        stac_path = "file:///" + stac_path

    return stac_path


def is_time_in_interval(time: Optional[datetime],
                        interval: List[datetime]) -> bool:
    return interval[0] <= time <= interval[1]


def is_not_intersection_bbox(bbox_1: List[float],
                             bbox_2: List[float]) -> bool:
    return bbox_1[0] > bbox_2[2] or bbox_1[2] < bbox_2[0] or\
           bbox_1[1] > bbox_2[3] or bbox_1[3] < bbox_2[1]


def is_item_match_by_time_pos(item: Item,
                              time_intervals: List[list[datetime, datetime]],
                              bboxes=List[list[float, float, float, float]]):
    for time_interval in time_intervals:
        if is_time_in_interval(item.datetime, time_interval):
            break
    else:
        return False

    for bbox in bboxes:
        if is_not_intersection_bbox(item.bbox, bbox):
            continue
        return True

    return False


def filter_catalog(catalog: Union[Catalog, Collection],
                   time_intervals: List[list[datetime, datetime]],
                   bboxes=List[list[float, float, float, float]]) -> List[Item]:
    res: List[Item] = []
    for item in catalog.get_items():
        if is_item_match_by_time_pos(item, time_intervals, bboxes):
            res.append(item)

    return res


def path_gen(pro_path: Optional[str],
             dir_name: Optional[str],
             filename: Optional[str] = None,
             file_extension: Optional[str] = None) -> Optional[str]:
    if file_extension is None:
        file_extension = dir_name
    if filename is None:
        data_dir, filename = path.split(pro_path)
    else:
        data_dir, _ = path.split(pro_path)

    data_dir = path.join(data_dir, "..", "..")
    filename = filename.rstrip(".pro")
    return path.normpath(path.join(data_dir, dir_name, filename + "." + file_extension))
