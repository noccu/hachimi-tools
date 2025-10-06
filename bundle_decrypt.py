from decrypt import decrypt_asset_bundle
from sys import argv
from meta_db_lib import MetaDb
from pathlib import Path
from const import GAME_META_FILE, GAME_ASSET_ROOT

def main():
    asset_hash = argv[1]

    db = MetaDb(GAME_META_FILE)
    asset_meta = db.cur.execute(f"SELECT n, e FROM a WHERE h = '{asset_hash}'").fetchone()
    if asset_meta is None:
        print(f"Bundle not found: {asset_hash}")
        return
    asset_path, asset_key = asset_meta
    bundle_path = GAME_ASSET_ROOT.joinpath(asset_hash[:2], asset_hash)
    if not bundle_path.is_file():
        print(f"Bundle {asset_hash} doesn't exist at {bundle_path}")
        return
    out_path = Path("decrypted_bundles", Path(asset_path).name)
    out_path.parent.mkdir(exist_ok=True)
    bundle_data = bundle_path.read_bytes()
    out_path.write_bytes(decrypt_asset_bundle(bundle_data, asset_key))
    print(f"Wrote {out_path.name}")

if __name__ == "__main__":
    main()