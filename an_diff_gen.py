from pathlib import Path
from unitypy_utils import find_texture_2d_by_name
from sys import argv
import UnityPy
from PIL import Image
from meta_db_lib import MetaDb
from png_diff_lib import png_diff
from utils import load_ignore_list
from decrypt import decrypt_asset_bundle
import const
from bundle_utils import get_bundle_data
import utils


def main():
    (an_dir, *target_dirs) = argv[1:]
    if an_dir == const.USE_TL_SRC_PATH:
        an_dir = utils.get_ld_assets_root("an_texture_sets")
    else:
        an_dir = Path(an_dir)

    meta = MetaDb(const.GAME_META_FILE)
    ignore_list = load_ignore_list(an_dir)

    for child in an_dir.iterdir():
        included = child.name in target_dirs if len(target_dirs) else True
        if not child.is_dir() or not included or not child.name.startswith("as_uMeshParam_fl_"):
            continue
        png_files = list(child.glob("*.png"))
        if len(png_files) == 0 or all(path.name.endswith(".diff.png") for path in png_files):
            continue

        base_name = child.name[len("as_uMeshParam_fl_") :]
        print(base_name)

        # Prefer source resource because if flash prefab + src rsrc exists then only src rsrc has the texture
        asset_path, asset_hash, asset_key = (
            meta.find_flash_source_resources(base_name) or meta.find_flash_prefab(base_name)
        ) or (None, None, None)

        if not asset_hash:
            print("[Warn] Asset not found, skipping")
            continue

        print(f"Bundle: {asset_hash} at {asset_path}")

        try:
            bundle_data = get_bundle_data(asset_hash)
        except FileNotFoundError as e:
            print(f"Couldn't find bundle {asset_hash}. {e}")
            return

        env = UnityPy.load(decrypt_asset_bundle(bundle_data, asset_key))
        for texture_path in png_files:
            if texture_path.name.endswith(".diff.png") or "/".join(texture_path.parts[-2:]) in ignore_list:
                continue

            if texture_path.is_file():
                rep_img = Image.open(texture_path)
                texture_name = texture_path.stem + "_C"

                texture = find_texture_2d_by_name(env, texture_name)
                if not texture:
                    print("[Error] Failed to find texture: " + texture_name)
                    continue

                diff_img = png_diff(texture.image, rep_img)
                texture_path.with_suffix(".diff.png").write_bytes(diff_img)


main()
