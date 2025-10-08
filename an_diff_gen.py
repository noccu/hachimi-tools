from pathlib import Path
from unitypy_utils import *
from sys import argv
import requests
import UnityPy
from PIL import Image
from meta_db_lib import MetaDb
from png_diff_lib import png_diff
from utils import load_ignore_list
from decrypt import decrypt_asset_bundle
from const import GAME_META_FILE


def main():
    (an_dir, *target_dirs) = argv[1:]
    an_dir = Path(an_dir)

    meta = MetaDb(GAME_META_FILE)
    ignore_list = load_ignore_list(an_dir)

    for child in an_dir.iterdir():
        if child.is_dir() and child.name.startswith("as_uMeshParam_fl_"):
            if len(target_dirs) and child.name not in target_dirs:
                continue
            png_files = list(child.glob("*.png"))
            if len(png_files) == 0 or all(path.name.endswith(".diff.png") for path in png_files):
                continue

            base_name = child.name[len("as_uMeshParam_fl_"):]
            print(base_name)

            # Prefer source resource because if flash prefab + src rsrc exists then only src rsrc has the texture
            (asset_name, asset_hash, asset_key) = (meta.find_flash_source_resources(base_name) or meta.find_flash_prefab(base_name)) or (None, None)

            if not asset_hash:
                print("[Warn] Asset not found, skipping")
                continue

            print("Bundle: " + asset_name)

            bundle_path = meta.get_asset_bundle_path(asset_hash)
            if bundle_path.is_file():
                bundle_data = bundle_path.read_bytes()
                status = 200
            else:
                bundle_url = meta.get_asset_bundle_url(asset_hash)
                bundle_res = requests.get(bundle_url)
                bundle_data = bundle_res.content
                status = bundle_res.status_code
            if status == 200:
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
                        diff_path = texture_path.with_suffix(".diff.png")
                        diff_path.write_bytes(diff_img)
            else:
                print("Got status code {}".format(status))

main()