from pathlib import Path
from sys import argv

import UnityPy

import const
import utils
from bundle_utils import get_bundle_data
from decrypt import decrypt_asset_bundle
from meta_db_lib import MetaDb
from unitypy_utils import find_all_texture_2d


def main():
    out_dir, target_an_name = argv[1:]
    if out_dir == const.USE_TL_SRC_PATH:
        out_dir = utils.get_ld_assets_root("an_texture_sets")

    db = MetaDb(const.GAME_META_FILE)
    for asset_path, asset_hash, asset_key in db.findall_flash_assets(target_an_name):
        try:
            bundle_data = get_bundle_data(db, asset_hash)
        except FileNotFoundError as e:
            print(f"Bundle {asset_hash} not found.\n{e}")
            return

        asset_path = Path(asset_path)
        base_name = asset_path.name[asset_path.name.find("fl_") + 3:]
        print(f"Found: {base_name}")

        bundle = UnityPy.load(decrypt_asset_bundle(bundle_data, asset_key))
        # Game/Hachimi always looks for this name.
        out_path = Path(out_dir, f"as_uMeshParam_fl_{base_name}")
        tx_count = 0
        for an_img in find_all_texture_2d(bundle):
            tx_count += 1
            img_out_path = (out_path / an_img.name.removesuffix("_C")).with_suffix(".png")
            out_path.mkdir(parents=True, exist_ok=True)  # Only create dir if textures found.
            an_img.image.save(img_out_path, "PNG", compress_level=9)
            print(f"Wrote {img_out_path.name}")

        if tx_count == 0:
            print(f"No texture found in {asset_path}.")


if __name__ == "__main__":
    main()
