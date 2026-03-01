import UnityPy
from PIL import Image
from unitypy_utils import *
from pathlib import Path
from sys import argv
from meta_db_lib import MetaDb
import const
from decrypt import decrypt_asset_bundle
from bundle_utils import get_bundle_data
import oxipng
import io
import utils

def main():
    (old_meta_path, atlas_name, *mode) = argv[1:]
    diff_mode = len(mode) and mode[0] == "diff"
    old_meta_path = Path(old_meta_path)
    atlas_ld_root = utils.get_ld_assets_root("atlas")

    old_meta = MetaDb.from_unknown(old_meta_path)
    new_meta = MetaDb(const.GAME_META_FILE)
    if atlas_name == "all":
        print(f"Updating all atlas files in {atlas_ld_root}")
        root_path = Path(atlas_ld_root)
        files = root_path.glob("**/*.json")
        for file in files:
            diff_file = file.with_suffix(".diff.png")
            if diff_file.exists():
                update(atlas_ld_root, old_meta, new_meta, file.stem, True)
            else:
                update(atlas_ld_root, old_meta, new_meta, file.stem, False)
    else:
        update(atlas_ld_root, old_meta, new_meta, atlas_name, diff_mode)

def update(atlas_ld_root:str, old_meta:MetaDb, new_meta:MetaDb, atlas_name:str, diff_mode:bool):
    old_hash, old_key = old_meta.get_asset_hash_and_key(f"atlas/{atlas_name}/{atlas_name}_tex")
    new_hash, new_key = new_meta.get_asset_hash_and_key(f"atlas/{atlas_name}/{atlas_name}_tex")
    if old_hash is None or new_hash is None:
        print(f"A hash was not found. Old: {old_hash}. New: {new_hash}")
        return
    else:
        assert old_key is not None and new_key is not None

    old_bundle_data = decrypt_asset_bundle(get_bundle_data(old_meta, old_hash), old_key)
    new_bundle_data = decrypt_asset_bundle(get_bundle_data(new_meta, new_hash), new_key)

    old_env = UnityPy.load(old_bundle_data)
    new_env = UnityPy.load(new_bundle_data)

    new_texture = find_first_texture_2d(new_env)
    if not new_texture:
        print("[Error] Texture not found in new bundle (invalid or failed to load asset bundle)")
        return
    new_texture_im = new_texture.image

    old_sprites = read_sprites_to_dict(old_env)
    new_sprites = read_sprites_to_dict(new_env)

    if not old_sprites:
        print("[Error] No sprites found in old bundle")
        return

    if not new_sprites:
        print("[Error] No sprites found in new bundle")
        return

    old_atlas_path = Path(atlas_ld_root, atlas_name, f"{atlas_name}{'.diff' if diff_mode else ''}.png")
    old_atlas_im = Image.open(old_atlas_path)

    width = new_texture.m_Width
    height = new_texture.m_Height
    im = Image.new("RGBA", (width, height), None)
    for name, new_data in new_sprites.items():
        new_rect = new_data.m_Rect
        new_rect_coords = rect_to_coords(new_rect, height)

        # Prefer to use sprites from the old translated atlas
        source_im = None
        source_rect_coords = None
        old_data = old_sprites.get(name)
        if old_data:
            old_rect = old_data.m_Rect
            if old_rect.width == new_rect.width and old_rect.height == new_rect.height:
                source_rect_coords = rect_to_coords(old_rect, height)
                source_im = old_atlas_im
            else:
                print("[Warn] {} has changed its size, using new sprite instead".format(name))

        if not source_im or not source_rect_coords:
            # Ignore new sprites when updating diff
            if diff_mode:
                print("{}: skipped".format(name))
                continue

            print("{}: new".format(name))
            source_im = new_texture_im
            source_rect_coords = new_rect_coords
        else:
            print("{}: old".format(name))

        # Crop the source image to the sprite
        sprite_im = source_im.crop(source_rect_coords)

        # Paste sprite on new atlas
        im.paste(sprite_im, (new_rect_coords[0], new_rect_coords[1]))

    img_bytes = io.BytesIO()
    im.save(img_bytes, "PNG", compress_level=9)
    old_atlas_path.write_bytes(oxipng.optimize_from_memory(img_bytes.getvalue()))


main()
