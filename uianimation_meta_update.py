import json
from sys import argv
from meta_db_lib import MetaDb
import utils

def main():
    (windows_meta, android_meta) = argv[1:]

    windows_meta = MetaDb(windows_meta)
    android_meta = MetaDb(android_meta)
    anim_dir = utils.get_ld_assets_root("uianimation")

    for meta_path in anim_dir.rglob("*.json"):
        bundle_name = ("uianimation" / meta_path.relative_to(anim_dir)).as_posix()[:-5]
        windows_hash = windows_meta.get_asset_hash_and_key(bundle_name)
        android_hash = android_meta.get_asset_hash_and_key(bundle_name)

        print(bundle_name)

        if not windows_hash and not android_hash:
            print("[Warn] Asset not found, skipping")
            continue

        with open(meta_path) as f:
            meta = json.load(f)

        if windows_hash:
            meta["windows"] = {'bundle_name': windows_hash}
        else:
            print("[Warn] Asset not found for Windows")

        if android_hash:
            meta["android"] = {'bundle_name': android_hash}
        else:
            print("[Warn] Asset not found for Android")

        with open(meta_path, "w", encoding="utf-8", newline='\n') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

main()