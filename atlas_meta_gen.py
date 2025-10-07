from pathlib import Path
import json
from sys import argv
from meta_db_lib import MetaDb
import const


def main():
    (android_meta, atlas_dir) = argv[1:]

    windows_meta = MetaDb(const.GAME_META_FILE)
    android_meta = MetaDb(android_meta)

    for child in Path(atlas_dir).iterdir():
        if child.is_dir():
            bundle_name = "atlas/{0}/{0}".format(child.name)
            windows_hash, _ = windows_meta.get_asset_hash_and_key(bundle_name)
            android_hash, _ = android_meta.get_asset_hash_and_key(bundle_name)

            print(f"Processing: {bundle_name}")
            if not windows_hash and not android_hash:
                print("[Warn] Asset not found, skipping")
                continue

            meta = {}

            if windows_hash:
                meta["windows"] = {"bundle_name": windows_hash}
            else:
                print("[Warn] Asset not found for Windows")

            if android_hash:
                meta["android"] = {"bundle_name": android_hash}
            else:
                print("[Warn] Asset not found for Android")

            with open(child / f"{child.name}.json", "w", encoding="utf-8", newline="\n") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)


main()
