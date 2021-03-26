from pystac import Asset, Catalog, CatalogType, read_file
from services import add_assets, create_item, parse
import os
from pathlib import Path

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
        item = create_item(i_id=file_name,
                           metadata=b0)
        assets: list[Asset] = [
            Asset(href=path, media_type=".pro"),
            Asset(href=tiff_path, media_type=".tiff")
        ]
        add_assets(item, assets)

        catalog = self.root_catalog.get_child(str(b0["b0_common"]["satId"][0]))
        if catalog is None:
            catalog = Catalog(id=str(b0["b0_common"]["satId"][0]),
                              title=b0["b0_common"]["satName"][0].decode("utf-8"),
                              description=f"Catalog for satellite {b0['b0_common']['satName'][0].decode('utf-8')}")
            self.root_catalog.add_child(catalog, catalog.title)
        catalog.add_item(item)

    def save(self) -> None:
        self.root_catalog.normalize_hrefs(self.path)
        self.root_catalog.save(catalog_type=CatalogType.SELF_CONTAINED)


if __name__ == '__main__':
    gis_spot_stac = GisSpotStac(new_path="stac/")
    gis_spot_stac.add_pro_file(os.path.join(BASE_DIR, "database\\pro\\20060504_041254_NOAA_18.m.pro"))
    gis_spot_stac.save()
