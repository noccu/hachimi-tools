from decrypt import decrypt_asset_bundle
from sys import argv
from meta_db_lib import MetaDb
from pathlib import Path
from const import GAME_META_FILE, GAME_ASSET_ROOT

def main():
    target_asset_path = argv[1]

    db = MetaDb(GAME_META_FILE)
    asset_meta = db.find_flash_source_resources(target_asset_path) or db.find_flash_prefab(target_asset_path)
    if asset_meta is None:
        print(f"Bundle not found: {target_asset_path}")
        return
    asset_name, asset_hash, asset_key = asset_meta
    bundle_path = GAME_ASSET_ROOT.joinpath(asset_hash[:2], asset_hash)
    if not bundle_path.is_file():
        print(f"Bundle {asset_hash} doesn't exist at {bundle_path}")
        return
    out_path = Path("decrypted_bundles", Path(asset_name).name)
    out_path.parent.mkdir(exist_ok=True)
    bundle_data = bundle_path.read_bytes()
    out_path.write_bytes(decrypt_asset_bundle(bundle_data, asset_key))
    print(f"Wrote {out_path.name}")

if __name__ == "__main__":
    main()