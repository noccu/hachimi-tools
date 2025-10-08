from sys import argv
from png_diff_lib import png_diff
from PIL import Image
from pathlib import Path

def main():
    (old_path, new_path, out_path) = argv[1:]
    old_img = Image.open(old_path).convert("RGBA")
    new_img = Image.open(new_path).convert("RGBA")

    out_img = png_diff(old_img, new_img)
    Path(out_path).write_bytes(out_img)

main()