import const
import bundle_dl
from meta_db_lib import MetaDb


def get_bundle_data(meta: MetaDb, hash: str) -> bytes:
    bundle_path = meta.get_asset_bundle_path(hash)
    bk_path = const.DL_DIR / hash
    for p in (bundle_path, bk_path):
        try:
            data = p.read_bytes()
            break
        except FileNotFoundError:
            continue
    else:
        data = bundle_dl.download(meta, hash)
        if isinstance(data, int):
            raise FileNotFoundError(f"Tried download but got status code {data}.")
        bk_path.write_bytes(data)
    return data
