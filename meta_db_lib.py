import apsw
from const import GAME_ASSET_ROOT

DB_KEY = "9c2bab97bcf8c0c4f1a9ea7881a213f6c9ebf9d8d4c6a8e43ce5a259bde7e9fd"


class MetaDb:
    def __init__(self, path, encrypted=True):
        if encrypted:
            uri = f"file:{str(path)}?hexkey={DB_KEY}"
        else:
            uri = f"file:{str(path)}"
        self.db = apsw.Connection(uri, apsw.SQLITE_OPEN_URI | apsw.SQLITE_OPEN_READONLY)
        self.cur = self.db.cursor()

        try:
            res = self.cur.execute("SELECT n FROM c WHERE n = '//Android' OR n = '//Windows'")
            self.platform = res.fetchone()[0][2:]
        except Exception:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def get_asset_hash_and_key(self, name) -> tuple[str, int] | tuple[None, None]:
        res = self.cur.execute("SELECT h, e FROM a WHERE n = '{}'".format(name))
        return (res.fetchone() or (None, None))

    URL_FORMAT = "https://prd-storage-game-umamusume.akamaized.net/dl/resources/{}/assetbundles/{}/{}"
    def get_asset_bundle_url(self, asset_hash):
        return self.URL_FORMAT.format(self.platform, asset_hash[0:2], asset_hash)

    def get_asset_bundle_path(self, asset_hash):
        return GAME_ASSET_ROOT.joinpath(asset_hash[0:2], asset_hash)

    def get_asset_bundle_url_from_name(self, name):
        asset_hash, _ = self.get_asset_hash_and_key(name)
        if not asset_hash:
            return None

        return self.get_asset_bundle_url(asset_hash)

    def find_flash_prefab(self, base_name):
        return self.cur.execute("SELECT n, h, e FROM a WHERE n LIKE 'uianimation/flash/%/pf_fl_{}'".format(base_name)).fetchone() # (name, hash)

    def find_flash_source_resources(self, base_name):
        return self.cur.execute("SELECT n, h, e FROM a WHERE n LIKE 'sourceresources/flash/%/fl_{0}/meshparameter/as_umeshparam_fl_{0}'".format(base_name)).fetchone() # (name, hash)

    @classmethod
    def from_unknown(cls, path):
        try:
            return cls(path)
        except apsw.NotADBError:
            return cls(path, False)