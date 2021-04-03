import os

from backend.database.core import GisStac
from backend.database.settings import STAC_PATH, FILES_PATH
from backend.database.services import path_gen, normalize_stac_path

gis_stac = GisStac(normalize_stac_path(STAC_PATH))
if __name__ == '__main__':
    # Печатаем сам stac
    for ch in gis_stac.root_catalog.get_children():
        for it in ch.get_items():
            print(it.to_dict())
#     Для первой генерация по папке data
#     gis_stac = GisStac(new_path=STAC_PATH)
#     pro_dir = os.path.join(FILES_PATH, "pro")
#     for filename in os.listdir(pro_dir):
#         full_filename = os.path.join(pro_dir, filename)
#
#         gis_stac.add_item(full_filename,
#                           path_gen(full_filename, "geotiff", file_extension="tiff"),
#                           path_gen(full_filename, "img"))
#     gis_stac.save()
#     print("success")
