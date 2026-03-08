from pathlib import Path
from sys import argv

import UnityPy
from PIL import Image, ImageDraw
from UnityPy.classes import Sprite

import const
import utils
from bundle_utils import get_bundle_data
from decrypt import decrypt_asset_bundle
from meta_db_lib import MetaDb
from unitypy_utils import find_first_texture_2d, rect_to_coords


def main():
    (out_dir, atlas_name) = argv[1:]
    if out_dir == const.USE_TL_SRC_PATH:
        out_dir = utils.get_ld_assets_root("atlas")
    else:
        out_dir = Path(out_dir)
    meta = MetaDb(const.GAME_META_FILE)

    asset_path, hash, key = meta.find_atlas(atlas_name)
    bundle_data = decrypt_asset_bundle(get_bundle_data(meta, hash), key)
    env = UnityPy.load(bundle_data)

    texture = find_first_texture_2d(env)
    if not texture:
        print("[Error] Texture not found (invalid or failed to load asset bundle)")
        return

    width = texture.m_Width
    height = texture.m_Height
    im = Image.new("RGBA", (width, height), None)
    im_draw = ImageDraw.Draw(im, "RGBA")
    for obj in env.objects:
        if obj.type.name == "Sprite":
            data: Sprite = obj.read()
            coords = rect_to_coords(data.m_Rect, height)
            im_draw.rectangle(coords, "#ff00ff")

    base_name = Path(asset_path).name.removesuffix("_tex")
    out_path = out_dir / base_name / f"{base_name}_matte.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, "PNG", compress_level=9)
    print(f"Wrote: {out_path}")


main()
