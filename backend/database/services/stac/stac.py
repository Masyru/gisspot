from datetime import datetime, timedelta
from pystac import Asset, Catalog, Collection, Item
from typing import Union, Optional

from backend.database.services.pro_files import b0_proj_dt


def create_item(i_id: str,
                metadata: b0_proj_dt)\
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
               assets: Optional[list[Asset]])\
        -> None:
    assets_count = len(item.get_assets())

    for asset in assets:
        item.add_asset(str(assets_count), asset=asset)
        assets_count += 1


def is_matching_by_properties(stac_obj: Union[Item, Collection],
                              categories: Optional[dict])\
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
                    categories: dict)\
        -> list[Item]:
    res: list[Item] = []

    for child in catalog.get_children():
        if type(child) is Catalog:
            res += filter_children(child, categories)
        elif type(child) is Collection:
            res += filter_collection(child, categories)

    for item in catalog.get_items():
        if is_matching_by_properties(item, categories):
            res.append(item)

    return res


def filter_collection(collection: Optional[Collection],
                      categories: Optional[dict])\
        -> list[Item]:
    if is_matching_by_properties(collection, categories):
        return filter_children(collection, categories)
    return []
