from pathlib import Path
from sys import argv

import const
from bundle_utils import get_bundle_data
from decrypt import decrypt_asset_bundle
from meta_db_lib import MetaDb


def decrypt(bundle_data: Path | bytes, key: int, name: str):
    if isinstance(bundle_data, Path):
        try:
            bundle_data = bundle_data.read_bytes()
        except FileNotFoundError:
            print(f"Bundle for {name} doesn't exist at {bundle_data}")
            return

    out_path = const.DECRYPTED_BUNDLES_DIR / Path(name).name
    if out_path.is_file():
        print(f"Skipping existing: {name}")
        return
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_bytes(decrypt_asset_bundle(bundle_data, key))
    print(f"Wrote {out_path.name}")


def main():
    asset_hash_or_path, *asset_key = argv[1:]

    if len(asset_key):
        asset_key = int(asset_key[0])
        bundle_path = Path(asset_hash_or_path)
        decrypt(bundle_path, asset_key, bundle_path.name)
    else:
        db = MetaDb(const.GAME_META_FILE)
        # Path
        if any(s in asset_hash_or_path for s in ("/", "_", "%")):
            query = f"SELECT n, h, e FROM a WHERE n LIKE '%{asset_hash_or_path}%'"
            asset_meta = db.cur.execute(query)
            for asset_path, asset_hash, asset_key in asset_meta:
                decrypt(get_bundle_data(db, asset_hash), asset_key, asset_path)
            if "asset_path" not in locals():
                print(f"No bundles found: {asset_hash_or_path}")
        # Hash
        else:
            query = f"SELECT n, e FROM a WHERE h = '{asset_hash_or_path}'"
            asset_meta = db.cur.execute(query).fetchone()
            if asset_meta:
                asset_path, asset_key = asset_meta
                decrypt(get_bundle_data(db, asset_hash_or_path), asset_key, asset_path)
            else:
                print(f"Bundle not found: {asset_hash_or_path}")
        db.close()


if __name__ == "__main__":
    main()
