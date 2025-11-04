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
