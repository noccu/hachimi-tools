from sys import argv
from pathlib import Path
import requests
from meta_db_lib import MetaDb
import const


def download(meta: MetaDb, asset_hash) -> bytes | int:
    response = requests.get(meta.get_asset_bundle_url(asset_hash))
    status = response.status_code

    if status == 200:
        return response.content
    else:
        return status


def main():
    (bundle_name, *output_dir) = argv[1:]
    if len(output_dir):
        output_dir = Path(output_dir[0])
    else:
        output_dir = const.DL_DIR
    meta = MetaDb.from_unknown(const.GAME_META_FILE)
    asset_hash, _ = meta.get_asset_hash_and_key(bundle_name)
    if asset_hash is None:
        return
    print(f"Found hash: {asset_hash}")

    path = output_dir / asset_hash
    path = path.with_name(f"{path.name}_{asset_hash}")
    path.parent.mkdir(parents=True, exist_ok=True)
    asset_data = download(meta, asset_hash)
    if isinstance(asset_data, int):
        print(f"Failed download. Status code: {asset_data}")
        return

    path.write_bytes(asset_data)
    print("Done")


if __name__ == "__main__":
    main()
