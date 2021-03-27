from datetime import datetime, timedelta
from pystac import Asset, Catalog, Collection, Item
from typing import Union, Optional

from backend.database.services.pro_files import b0_proj_dt

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
               assets: Optional[list[Asset]]) \
        -> None:
    assets_count = len(item.get_assets())

    for asset in assets:
        item.add_asset(str(assets_count), asset=asset)
        assets_count += 1


def is_matching_by_properties(stac_obj: Union[Item, Collection],
                              categories: Optional[dict]) \
        -> bool:
    properties: dict = stac_obj.properties

    for category, value in categories.items():
        item_value: str = properties.get(category, None)
        if item_value is None:
            continue  # TODO: Может НЕ нужно брать с пропущенной категорией

        if item_value != value:
            break

    else:
        return True
    return False


def filter_children(catalog: Catalog,
                    categories: dict,
                    special_filters: Optional[dict] = {}) \
        -> list[Item]:
    res: list[Item] = []

    for child in catalog.get_children():
        if type(child) is Catalog:
            res += filter_children(child, categories)
        elif type(child) is Collection:
            res += filter_collection(child, categories)

    for item in catalog.get_items():
        if not is_matching_by_properties(item, categories):
            continue

        if not is_matching_by_extent(item.datetime, item.bbox,
                                     special_filters.get("datetime", None),
                                     special_filters.get("bbox", None)):
            continue

        res.append(item)

    return res


def filter_collection(collection: Optional[Collection],
                      categories: Optional[dict],
                      special_filters: Optional[dict] = {}) \
        -> list[Item]:
    if not is_matching_by_properties(collection, categories):
        return []

    if not is_matching_by_extent(collection.extent.temporal.intervals,
                                 collection.extent.spatial.bboxes,
                                 special_filters.get("datetime", None),
                                 special_filters.get("bbox", None)):
        return []

    return filter_children(collection, categories)


def is_matching_by_extent(collection_datetime: Optional[list[datetime, datetime]],
                          collection_bbox: Optional[list[float, float, float, float]],
                          extent_datetime: Union[list[datetime, datetime], None],
                          extent_bbox: Union[list[float, float, float, float], None])\
        -> bool:
    if extent_datetime is not None:
        if is_not_intersection_timelines(collection_datetime, extent_datetime):
            return False

    if extent_bbox is not None:
        if is_not_intersection_bbox(collection_bbox, extent_bbox):
            return False

    return True


def is_not_intersection_bbox(bbox_1: Optional[list[float, float, float, float]],
                             bbox_2: Optional[list[float, float, float, float]]) -> bool:
    return bbox_1[0] > bbox_2[2] or bbox_1[2] < bbox_2[0] or\
           bbox_1[1] > bbox_2[3] or bbox_1[3] < bbox_2[1]


def is_not_intersection_timelines(timeline_1: Optional[list[datetime, datetime]],
                                  timeline_2: Optional[list[datetime, datetime]]):
    return timeline_1[0] > timeline_2[1] or timeline_2[1] < timeline_2[0]  # TODO: Упадёт если попадёт None


def converter_datetime(field: Optional[list[str, str]]):
    return [datetime.fromisoformat(field[0]), datetime.fromisoformat(field[1])]


def processing_filters(filters: dict) -> (dict, dict):
    base_filters = {}
    special_filters = {}

    for filter_key, filter_value in filters.items():
        if converter := SPACIAL_CATEGORIES.get(filter_key, None) is not None:
            special_filters[filter_key] = converter(filter_value)

        else:
            base_filters[filter_key] = filter_value

    return base_filters, special_filters


SPACIAL_CATEGORIES = {"datetime": converter_datetime, "bbox": lambda el: el}
