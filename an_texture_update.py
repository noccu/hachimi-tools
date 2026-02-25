import io
from pathlib import Path
from sys import argv

import oxipng
import UnityPy
from PIL import Image

import const
from bundle_utils import get_bundle_data
from decrypt import decrypt_asset_bundle
from meta_db_lib import MetaDb
from unitypy_utils import find_first_texture_2d, parse_texture_sprites, rect_to_coords


def main():
    (ld_root, old_meta_path, tx_name, *mode) = argv[1:]
    diff_mode = len(mode) and mode[0] == "diff"
    old_meta_path = Path(old_meta_path)
    tx_root_path = Path(ld_root, "assets", "an_texture_sets")

    old_meta = MetaDb.from_unknown(old_meta_path)
    new_meta = MetaDb(const.GAME_META_FILE)
    if tx_name == "all":
        print(f"Updating all an_textures in {tx_root_path}")
        files = tx_root_path.rglob(f"*{'.diff' if diff_mode else ''}.png")
    else:
        files = tx_root_path.glob(f"*{tx_name}/*{'.diff' if diff_mode else ''}.png")

    for file in files:
        if not diff_mode and "diff" in file.name:
            continue
        print(f"-- Updating {tx_name} --")
        update(old_meta, new_meta, file, diff_mode)
    print("Finished.")


def update(old_meta: MetaDb, new_meta: MetaDb, cur_file: Path, diff_mode: bool):
    tx_name = cur_file.parent.name[len("as_uMeshParam_fl_") :]

    old_bundle = old_meta.find_flash_source_resources(tx_name) or old_meta.find_flash_prefab(tx_name)
    new_bundle = new_meta.find_flash_source_resources(tx_name) or new_meta.find_flash_prefab(tx_name)
    if old_bundle is None:
        print(f"{tx_name}: Old bundle was not found.")
        return
    if new_bundle is None:
        print(f"{tx_name}: New bundle was not found.")
        return

    _, old_hash, old_key = old_bundle
    _, new_hash, new_key = new_bundle

    old_bundle_data = decrypt_asset_bundle(get_bundle_data(old_meta, old_hash), old_key)
    new_bundle_data = decrypt_asset_bundle(get_bundle_data(new_meta, new_hash), new_key)

    old_env = UnityPy.load(old_bundle_data)
    new_env = UnityPy.load(new_bundle_data)

    new_texture = find_first_texture_2d(new_env)
    if not new_texture:
        print("[Error] Texture not found in new bundle (invalid or failed to load asset bundle)")
        return
    new_texture_im = new_texture.image

    old_sprites = parse_texture_sprites(old_env)
    new_sprites = parse_texture_sprites(new_env)
    if not old_sprites:
        print("[Error] No sprites found in old bundle")
        return
    if not new_sprites:
        print("[Error] No sprites found in new bundle")
        return

    old_tx_im = Image.open(cur_file)
    width = new_texture.m_Width
    height = new_texture.m_Height
    new_img = Image.new("RGBA", (width, height), None)
    for name, new_rect in new_sprites.items():
        new_rect_coords = rect_to_coords(new_rect, height)
        source_im = None
        source_rect_coords = None
        is_rotated = False

        # Prefer to use sprites from the old translated atlas
        old_rect = old_sprites.get(name)
        if old_rect:
            is_rotated = getattr(old_rect, "rotated") != getattr(new_rect, "rotated")
            if (old_rect.width == new_rect.width and old_rect.height == new_rect.height) or (
                is_rotated and old_rect.width == new_rect.height and old_rect.height == new_rect.width
            ):
                source_rect_coords = rect_to_coords(old_rect, height)
                source_im = old_tx_im
            else:
                print(f"[Warn] {name} has changed its size: {vars(old_rect)} -> {vars(new_rect)}")

        # Crop the source image to the sprite
        if source_im:
            print(f"{name}: old{' (rotated)' if is_rotated else ''}")
            sprite_im = source_im.crop(source_rect_coords)
            if is_rotated:
                sprite_im = sprite_im.transpose(Image.Transpose.ROTATE_90)
        else:
            # Ignore new sprites when updating diff
            if diff_mode:
                print(f"{name}: skipped")
                continue
            print(f"{name}: new")
            sprite_im = new_texture_im.crop(new_rect_coords)

        # Paste sprite on new atlas
        new_img.paste(sprite_im, (new_rect_coords[0], new_rect_coords[1]))

    img_bytes = io.BytesIO()
    new_img.save(img_bytes, "PNG", compress_level=9)
    cur_file.write_bytes(oxipng.optimize_from_memory(img_bytes.getvalue()))


main()
