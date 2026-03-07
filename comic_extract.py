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
        out_dir = utils.get_ld_assets_root("textures")
    else:
        out_dir = Path(out_dir)

    db = MetaDb(const.GAME_META_FILE)
    for asset_meta in db.findall_comic(target_name):
        extract(db, asset_meta, out_dir)


def extract(db: MetaDb, asset_meta: tuple[str, str, str], out_dir: Path):
    asset_path, asset_hash, asset_key = asset_meta
    try:
        bundle_data = get_bundle_data(db, asset_hash)
    except FileNotFoundError as e:
        print(f"Bundle {asset_hash} not found. {e}")
        return
    bundle = UnityPy.load(decrypt_asset_bundle(bundle_data, asset_key))
    out_path = Path(out_dir, asset_path).parent
    out_path.mkdir(parents=True, exist_ok=True)

    comic_img = find_first_texture_2d(bundle)
    if not comic_img:
        print(f"No texture found in bundle {asset_hash} for {asset_path}.")
    real_size = (round(comic_img.image.width * (4 / 3)), comic_img.image.height)
    resized_img = comic_img.image.resize(real_size)
    comic_img.image.save((out_path / f"{comic_img.name}.png"), "PNG", compress_level=9)
    resized_img.save((out_path / f"{comic_img.name}_scaled.png"), "PNG", compress_level=9)

    print(f"Wrote {comic_img.name} to {out_path}")


if __name__ == "__main__":
    main()
