from os import environ
from pathlib import Path

GAME_ROOT = environ.get("UMA_DATA_DIR")
if GAME_ROOT:
    GAME_ROOT = Path(GAME_ROOT)
else:
    GAME_ROOT = Path(environ["LOCALAPPDATA"], "..", "LocalLow", "Cygames", "umamusume").resolve()

GAME_ASSET_ROOT = GAME_ROOT.joinpath("dat")
GAME_META_FILE = GAME_ROOT.joinpath("meta")
GAME_MASTER_FILE = GAME_ROOT.joinpath("master", "master.mdb")

DL_DIR = Path("dl")
