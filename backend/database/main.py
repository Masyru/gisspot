from pystac import Asset, Catalog, Collection, CatalogType, read_file, \
    Extent, SpatialExtent, TemporalExtent, Item
from services import parse
import os
from pathlib import Path
from typing import Optional

from .services import stac

BASE_DIR = Path(__file__).resolve().parent.parent


class GisSpotStac:
    def __init__(self, old_catalog_path=None, new_path=None) -> None:
        if old_catalog_path is None:
            if new_path is None:
                new_path = ""

            self.path: str = new_path
            self.root_catalog: Catalog = Catalog(id="GisSpot-root-catalog",
                                        title="GisSpot-root-catalog",
                                        description="Root catalog on GisSpot server")

        else:
            stac_obj = read_file(old_catalog_path)

            if type(stac_obj) is Catalog:
                self.root_catalog: Catalog = stac_obj

            else:
                raise TypeError("old_catalog_path must be path to STAC catalog")

            if new_path is None:
                self.path: str = self.root_catalog.get_self_href()

            else:
                self.path: str = new_path

    def add_pro_file(self, path: str) -> None:
        if not path.endswith(".pro"):
            print("file is not pro")
            return
        file_name = path.split("/")[-1].rstrip(".pro")
        tiff_path = ""  # TODO: gen tiff file from pro file;

        b0, data = parse(path)
        item = stac.create_item(i_id=file_name,
                           metadata=b0)
        assets: list[Asset] = [
            Asset(href=path, media_type=".pro"),
            Asset(href=tiff_path, media_type=".tiff")
        ]
        stac.add_assets(item, assets)
        extent = Extent(spatial=SpatialExtent([-180, -90, 180, 90]),  # TODO: Реальный Extent
                        temporal=TemporalExtent(["2009-01-01T00:00:00Z", None]))

        catalog = self.root_catalog.get_child(str(b0["b0_common"]["satId"][0]))
        if catalog is None:
            catalog = Collection(id=str(b0["b0_common"]["satId"][0]),
                                 title=b0["b0_common"]["satName"][0].decode("utf-8"),
                                 description=f"Catalog for satellite {b0['b0_common']['satName'][0].decode('utf-8')}",
                                 extent=extent)
            self.root_catalog.add_child(catalog, catalog.title)
        catalog.add_item(item)

    def save(self) -> None:
        self.root_catalog.normalize_hrefs(self.path)
        self.root_catalog.save(catalog_type=CatalogType.SELF_CONTAINED)

    def filter(self,
               filters: Optional[dict]) \
            -> list[Item]:
        return stac.filter_children(self.root_catalog, filters)


if __name__ == '__main__':
    gis_spot_stac = GisSpotStac(new_path="stac/")
    gis_spot_stac.add_pro_file(os.path.join(BASE_DIR, "database\\pro\\20060504_041254_NOAA_18.m.pro"))
    gis_spot_stac.save()
