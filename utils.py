import json
from pathlib import Path

def load_ignore_list(dir_path):
    try:
        f = open(dir_path / ".gitignore", "r")
        print("Loading ignore list from .gitignore")
        return {s[1:] for s in f.readlines() if s[0] == "!" and not "*" in s}
    except:
        return {}

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline='\n') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Config

def open_config():
    cfg_path = Path("config.json")
    try:
        cfg = read_json(cfg_path)
    except FileNotFoundError:
        print("No config file found, creating...")
        cfg = create_config()
        write_json(cfg_path, cfg)
    return cfg


def create_config():
    return {"ld_root": input("Set localized_data root folder: ").strip()}


def get_ld_root(*add_path):
    cfg = open_config()
    try:
        val = Path(cfg["ld_root"], *add_path)
        return val
    except KeyError:
        print("Error: Set ld_root in config")
        raise SystemExit


def get_ld_assets_root(*add_path):
    return get_ld_root("assets", *add_path)
