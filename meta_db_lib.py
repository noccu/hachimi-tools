import apsw
from const import GAME_ASSET_ROOT, IS_GLOBAL

DB_KEY = "9c2bab97bcf8c0c4f1a9ea7881a213f6c9ebf9d8d4c6a8e43ce5a259bde7e9fd"
DB_KEY_GLOBAL = "A713A5C79DBC9497C0A88669"


class MetaDb:
    def __init__(self, path, encrypted=True, key=None):
        if encrypted:
            key = key or (DB_KEY_GLOBAL if IS_GLOBAL else DB_KEY)
            uri = f"file:{str(path)}?hexkey={key}"
        else:
            uri = f"file:{str(path)}"
        self.db = apsw.Connection(uri, apsw.SQLITE_OPEN_URI | apsw.SQLITE_OPEN_READONLY)
        self.cur = self.db.cursor()

        try:
            res = self.cur.execute("SELECT n FROM c WHERE n = '//Android' OR n = '//Windows'")
            self.platform:str = res.fetchone()[0][2:]
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

    def findall_flash_prefab(self, base_name):
        return self.db.execute(f"SELECT n, h, e FROM a WHERE n LIKE 'uianimation/flash/%/pf_fl_%{base_name}%'")

    def find_flash_prefab(self, base_name):
        return self.findall_flash_prefab(base_name).fetchone()

    def findall_flash_source_resources(self, base_name):
        return self.cur.execute("SELECT n, h, e FROM a WHERE n LIKE 'sourceresources/flash/%/fl_%{0}%/meshparameter/as_umeshparam_fl_%{0}%'".format(base_name))

    def find_flash_source_resources(self, base_name) -> tuple[str, str, str] | None:
        return self.findall_flash_source_resources(base_name).fetchone()

    def findall_flashcombine_prefab(self, base_name):
        return self.db.execute(f"SELECT n, h, e FROM a WHERE n LIKE 'uianimation/flashcombine/%/fa_%{base_name}%'")

    def find_flashcombine_prefab(self, base_name):
        return self.findall_flashcombine_prefab(base_name).fetchone()

    def find_flash_uparam(self, base_name) -> tuple[str, str, str] | None:
        return self.db.execute(f"SELECT n, h, e FROM a WHERE n LIKE 'sourceresources/flash/%/as_uparam_fl_%{base_name}%'").fetchone()

    def findall_atlas(self, base_name):
        return self.db.execute(f"SELECT n, h, e FROM a WHERE m = 'atlas' AND n LIKE 'atlas/%{base_name}%_tex'")

    def find_atlas(self, base_name) -> tuple[str, str, str] | None:
        return self.findall_atlas(base_name).fetchone()

    def findall_comic(self, base_name):
        return self.db.execute(f"SELECT n, h, e FROM a WHERE n LIKE 'outgame/comic/tex_comic_{base_name}%'")

    def find_comic(self, base_name)  -> tuple[str, str, str] | None:
        return self.findall_comic(base_name).fetchone()

    @classmethod
    def from_unknown(cls, path):
        try:
            return cls(path)
        except apsw.NotADBError:
            return cls(path, False)