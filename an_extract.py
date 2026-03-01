from decrypt import decrypt_asset_bundle
from sys import argv
from meta_db_lib import MetaDb
from pathlib import Path
import const
import UnityPy
from unitypy_utils import find_all_texture_2d
from bundle_utils import get_bundle_data
import utils


def main():
    out_dir, target_an_name = argv[1:]
    if out_dir == const.USE_TL_SRC_PATH:
        out_dir = utils.get_ld_assets_root("an_texture_sets")

    db = MetaDb(const.GAME_META_FILE)
    asset_meta = db.find_flash_source_resources(target_an_name) or db.find_flash_prefab(target_an_name)
    if asset_meta is None:
        print(f"No matching bundle found for {target_an_name}")
        return
    asset_path, asset_hash, asset_key = asset_meta

    try:
        bundle_data = get_bundle_data(db, asset_hash)
    except FileNotFoundError as e:
        print(f"Bundle {asset_hash} not found. {e}")
        return

    bundle = UnityPy.load(decrypt_asset_bundle(bundle_data, asset_key))
    asset_path = Path(asset_path)
    out_path = Path(out_dir, asset_path.name)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for an_img in find_all_texture_2d(bundle):
        img_out_path = out_path.joinpath(an_img.name.removesuffix("_C")).with_suffix(".png")
        an_img.image.save(img_out_path, "PNG", compress_level=9)
        print(f"Wrote {img_out_path.name}")

    if "an_img" not in locals():
        print(f"No texture found in bundle {asset_hash}.")
    else:
        print("Done.")


if __name__ == "__main__":
    main()
