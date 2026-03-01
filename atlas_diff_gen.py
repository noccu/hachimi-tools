from pathlib import Path
from unitypy_utils import *
from sys import argv
from const import GAME_META_FILE
import UnityPy
from PIL import Image
from meta_db_lib import MetaDb
from png_diff_lib import png_diff
from utils import load_ignore_list, get_ld_assets_root
from decrypt import decrypt_asset_bundle
import const
from bundle_utils import get_bundle_data

def main():
    (atlas_dir, *target_dirs) = argv[1:]
    if atlas_dir == const.USE_TL_SRC_PATH:
        atlas_dir = get_ld_assets_root("atlas")
    else:
        atlas_dir = Path(atlas_dir)

    meta = MetaDb(GAME_META_FILE)
    ignore_list = load_ignore_list(atlas_dir)

    for child in atlas_dir.iterdir():
        if child.is_dir():
            if len(target_dirs) and child.name not in target_dirs:
                continue
            texture_path = child / (child.name + ".png")
            if "/".join(texture_path.parts[-2:]) in ignore_list:
                continue

            if texture_path.is_file():
                rep_img = Image.open(texture_path)

                bundle_name = "atlas/{0}/{0}_tex".format(child.name)
                print(bundle_name)

                bundle_hash, bundle_key = meta.get_asset_hash_and_key(bundle_name)
                if not bundle_hash:
                    print("[Warn] Asset not found, skipping")
                    continue

                try:
                    bundle_data = get_bundle_data(meta, bundle_hash)
                except FileNotFoundError as e:
                    print(f"Bundle {bundle_hash} not found.\n{e}")
                    continue

                env = UnityPy.load(decrypt_asset_bundle(bundle_data, bundle_key))
                texture = find_first_texture_2d(env)
                if not texture:
                    print("[Error] Texture not found (invalid or failed to load asset bundle)")
                    continue

                diff_img = png_diff(texture.image, rep_img)
                diff_path = child / f"{child.name}.diff.png"
                diff_path.write_bytes(diff_img)

main()