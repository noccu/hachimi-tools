from pathlib import Path
from sys import argv

import UnityPy

import const
import utils
from bundle_utils import get_bundle_data
from decrypt import decrypt_asset_bundle
from meta_db_lib import MetaDb
from unitypy_utils import find_first_texture_2d


def main():
    out_dir, target_name = argv[1:]
    if out_dir == const.USE_TL_SRC_PATH:
        out_dir = utils.get_ld_assets_root("atlas")

    db = MetaDb(const.GAME_META_FILE)
    for asset_path, asset_hash, asset_key in db.findall_atlas(target_name):
        try:
            bundle_data = get_bundle_data(db, asset_hash)
        except FileNotFoundError as e:
            print(f"Bundle {asset_hash} not found. {e}")
            return

        bundle = UnityPy.load(decrypt_asset_bundle(bundle_data, asset_key))
        base_name = Path(asset_path).name.removesuffix("_tex")
        out_path = Path(out_dir, base_name)
        out_path.mkdir(parents=True, exist_ok=True)

        atlas_img = find_first_texture_2d(bundle)
        img_out_path = out_path.joinpath(base_name).with_suffix(".png")
        atlas_img.image.save(img_out_path, "PNG", compress_level=9)
        print(f"Wrote {img_out_path.name}")
        print("Done.")


if __name__ == "__main__":
    main()
