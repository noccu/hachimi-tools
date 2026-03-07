import UnityPy
from UnityPy.classes import Texture2D, Sprite
from UnityPy.math import Rectangle
from typing import Generator


def find_all_texture_2d(env: UnityPy.Environment) -> Generator[Texture2D]:
    for obj in env.objects:
        if obj.type.name == "Texture2D":
            yield obj.read()


def find_first_texture_2d(env: UnityPy.Environment):
    return next(find_all_texture_2d(env), None)


def read_sprites_to_dict(env: UnityPy.Environment) -> dict[str, Sprite]:
    d = {}
    for obj in env.objects:
        if obj.type.name == "Sprite":
            data: Sprite = obj.read()
            d[data.m_Name] = data
    return d


def rect_to_coords(rect: Rectangle, max_y: int):
    x0 = rect.x
    y0 = max_y - rect.y - rect.height
    x1 = rect.x + rect.width
    y1 = max_y - rect.y
    return (int(x0), int(y0), int(x1), int(y1))


def find_texture_2d_by_name(env: UnityPy.Environment, name: str) -> Texture2D:
    for obj in env.objects:
        if obj.type.name == "Texture2D":
            data = obj.read()
            if data.name == name:
                return data


def find_monobehaviour(env: UnityPy.Environment):
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            return obj.read_typetree()


def parse_texture_sprites(env: UnityPy.Environment) -> dict[str, Rectangle]:
    metadata = find_monobehaviour(env)
    if metadata is None:
        return

    d = {}
    metadata: dict = metadata.get("_meshParameterGroupList")[0]
    tx_size: dict = metadata.get("_textureSetSize")
    tx_list: list[dict] = metadata.get("_meshInfoParameterList")
    for tx in tx_list:
        w = tx["_uvSize"]["x"] * tx_size["x"]
        h = tx["_uvSize"]["y"] * tx_size["y"]
        x = tx["_uvOffset"]["x"] * tx_size["x"]
        y = tx["_uvOffset"]["y"] * tx_size["y"]
        rect = Rectangle(x, y, w, h).round()
        setattr(rect, "rotated", tx["_rotated"] == 1)
        d[tx["_textureName"]] = rect

    return d
