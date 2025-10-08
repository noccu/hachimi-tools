from decrypt import decrypt_asset_bundle
from sys import argv
from meta_db_lib import MetaDb
from pathlib import Path
import const

def main():
    asset_hash_or_path, *asset_key = argv[1:]

    if len(asset_key):
        asset_key = int(asset_key[0])
        bundle_path = Path(asset_hash_or_path)
        asset_path = bundle_path.name
    else:
        db = MetaDb(const.GAME_META_FILE)
        if "/" in asset_hash_or_path:
            query = f"SELECT n, e FROM a WHERE n LIKE '%{asset_hash_or_path}%'"
        else:
            query = f"SELECT n, e FROM a WHERE h = '{asset_hash_or_path}'"
        asset_meta = db.cur.execute(query).fetchone()
        db.close()
        if asset_meta is None:
            print(f"Bundle not found: {asset_hash_or_path}")
            return
        asset_path, asset_key = asset_meta
        bundle_path = db.get_asset_bundle_path(asset_hash_or_path)

    if not bundle_path.is_file():
        print(f"Bundle {asset_hash_or_path} doesn't exist at {bundle_path}")
        return
    out_path = const.DECRYPTED_BUNDLES_DIR / Path(asset_path).name
    out_path.parent.mkdir(exist_ok=True)
    bundle_data = bundle_path.read_bytes()
    out_path.write_bytes(decrypt_asset_bundle(bundle_data, asset_key))
    print(f"Wrote {out_path.name}")

if __name__ == "__main__":
    main()