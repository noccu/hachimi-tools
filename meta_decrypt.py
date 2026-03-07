from pathlib import Path
import argparse
from meta_db_lib import MetaDb
from const import GAME_META_FILE, DECRYPTED_METAS_DIR
from datetime import date


def parse_args():
    parser = argparse.ArgumentParser(
        description="Decrypt Umamusume game meta SQLite DB"
    )
    parser.add_argument(
        "src", nargs="?", type=Path, help="Path to encrypted DB (default: <Uma data dir>/meta)"
    )
    parser.add_argument(
        "dst", nargs="?", help="Path to save decrypted DB (default: decrypted_metas/<src name>_<iso date>.sqlite)"
    )
    parser.add_argument("--key", "-k", help="Hex key (default: hardcoded key)")
    # parser.add_argument(
    #     "--cipher", dest="cipher", type=int, default=3, help="sqlite3mc cipher index to set (default: 3)"
    # )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.src:
        args.src = GAME_META_FILE
    if not args.dst:
        DECRYPTED_METAS_DIR.mkdir(exist_ok=True)
        args.dst = DECRYPTED_METAS_DIR / f"{args.src.stem}_{date.today().isoformat()}.sqlite"

    print(f"Decrypting {args.src} to {args.dst}")
    meta = MetaDb(args.src, key=args.key)
    meta.cur.close()  # Old class impl detail gets in the way.
    try:
        meta.db.execute(f"VACUUM INTO 'file:{str(args.dst)}?key='")
    finally:
        meta.close()
    # Another method: sqlcipher_export()


if __name__ == "__main__":
    main()
