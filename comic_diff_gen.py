from io import BytesIO
from pathlib import Path
from sys import argv

import UnityPy
from PIL import Image

import const
import utils
from bundle_utils import get_bundle_data
from decrypt import decrypt_asset_bundle
from meta_db_lib import MetaDb
from png_diff_lib import get_optimized_png, png_diff
from unitypy_utils import find_first_texture_2d
from utils import load_ignore_list


def main():
    (in_dir, fuzzy_thresh, *target_names) = argv[1:]
    out_dir = utils.get_ld_assets_root("textures")
    if in_dir == const.USE_TL_SRC_PATH:
        in_dir = out_dir
    else:
        in_dir = Path(in_dir)

    meta = MetaDb(const.GAME_META_FILE)
    ignore_list = load_ignore_list(in_dir)

    for img_path in in_dir.rglob("tex_comic_*.png"):
        if (
            img_path.stem.endswith(".diff")
            or "_thumb" in img_path.stem
            or (len(target_names) and not any(name in img_path.stem for name in target_names))
            or "/".join(img_path.parts[-2:]) in ignore_list
        ):
            continue
        write_diff(meta, img_path, out_dir, fuzzy_thresh)


def write_diff(meta: MetaDb, img_path: Path, out_dir: Path, fuzzy_thresh: float):
    base_name = img_path.stem[len("tex_comic_") :]
    print(base_name)

    asset_path, asset_hash, asset_key = meta.find_comic(base_name) or (None, None, None)
    if asset_hash is None:
        print("[Warn] Asset not found, skipping")
        return
    print(f"Bundle: {asset_hash} at {asset_path}")

    try:
        bundle_data = get_bundle_data(meta, asset_hash)
    except FileNotFoundError as e:
        print(f"Couldn't find bundle {asset_hash}.\n{e}")
        return

    env = UnityPy.load(decrypt_asset_bundle(bundle_data, asset_key))
    texture = find_first_texture_2d(env)
    if not texture:
        print(f"[Error] Failed to find texture: {base_name}")
        return

    rep_img = Image.open(img_path)
    if rep_img.size == texture.image.size:
        fuzzy_thresh = 0.0
    else:
        rep_img = rep_img.resize(texture.image.size)
    diff_img = png_diff(texture.image, rep_img, fuzzy_thresh)

    out_path = out_dir.joinpath(asset_path).with_suffix(".diff.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(diff_img)
    # Create thumb. Simplified instead of re-diffing because it likely
    # doesn't matter and would ideally require a separate edit anyway.
    thumb = Image.open(BytesIO(diff_img))
    thumb_size = (round(texture.image.width / 2), round(texture.image.height / 4))
    thumb_diff = get_optimized_png(thumb.resize(thumb_size))
    out_path.with_name(out_path.name.replace("comic_", "comic_thumb_")).write_bytes(thumb_diff)
    print(f"Wrote {base_name}")


if __name__ == "__main__":
    main()
