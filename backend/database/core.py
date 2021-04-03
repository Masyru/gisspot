from pystac import Asset, Catalog, Collection, CatalogType, read_file, \
    Extent, SpatialExtent, TemporalExtent, Item
from datetime import datetime
from typing import List, Optional

import sys
sys.path.append("../../")
from backend.database.services import parse, stac, normalize_stac_path, filter_catalog


class GisStac:
    def __init__(self, old_catalog_path: str = None, new_path: str = None) -> None:
        if old_catalog_path is None:
            if new_path is None:
                new_path = ""

            self.path: str = new_path
            self.root_catalog: Catalog = Catalog(id="GisSpot-root-catalog",
                                                 title="GisSpot-root-catalog",
                                                 description="Root catalog on GisSpot server")

        else:
            old_catalog_path = normalize_stac_path(old_catalog_path)
            print(old_catalog_path)
            stac_obj = read_file(old_catalog_path)

            if type(stac_obj) is Catalog:
                self.root_catalog: Catalog = stac_obj

            else:
                raise TypeError("old_catalog_path must be path to STAC catalog")

            if new_path is None:
                self.path: str = self.root_catalog.get_self_href()

            else:
                self.path: str = new_path

    def add_item(self, path_pro: Optional[str], path_tiff: Optional[str],
                 path_img: Optional[str]) -> None:
        assert path_pro.endswith(".pro")
        file_name = path_pro.split("\\")[-1].rstrip(".pro")
        print(file_name)
        b0, data = parse(path_pro)
        item: Item = stac.create_item(i_id=file_name, metadata=b0)
        assets: list[Asset] = [
            Asset(href=path_pro, media_type="pro")
        ]
        if path_tiff is not None:
            assets.append(Asset(href=path_tiff, media_type="geotiff"))
        if path_img is not None:
            assets.append(Asset(href=path_img, media_type="img"))
        stac.add_assets(item, assets)

        catalog = self.root_catalog.get_child(str(b0["b0_common"]["satId"][0]))
        if catalog is None:
            extent = Extent(spatial=SpatialExtent([[-180, -90, 180, 90]]),  # TODO: Реальный Extent
                            temporal=TemporalExtent([[
                                datetime.strptime("2009-01-01T00:00:00.000000", "%Y-%m-%dT%H:%M:%S.%f"),
                                None]]))
            catalog = Collection(id=str(b0["b0_common"]["satId"][0]),
                                 title=b0["b0_common"]["satName"][0].decode("utf-8"),
                                 description=f"Catalog for satellite "
                                             f"{b0['b0_common']['satName'][0].decode('utf-8')}",
                                 extent=extent)
            self.root_catalog.add_child(catalog, catalog.title)

        # update_collection_extent(item, catalog)

        catalog.add_item(item)

    def save(self) -> None:
        self.root_catalog.normalize_hrefs(self.path)
        self.root_catalog.save(catalog_type=CatalogType.SELF_CONTAINED)

    def filter(self, time_intervals: List[list[datetime, datetime]],
               bboxes=List[list[float, float, float, float]]) -> List[Item]:
        res: List[Item] = []
        for catalog in self.root_catalog.get_children():
            res += filter_catalog(catalog, time_intervals, bboxes)

        return res
