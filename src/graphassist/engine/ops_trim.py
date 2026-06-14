"""トリミング・flatten。"""

from __future__ import annotations

from PIL import Image

from graphassist.engine.colors import parse_color
from graphassist.schema.ops import FlattenOp, TrimOp


def trim_image(img: Image.Image, op: TrimOp) -> Image.Image:
    rgba = img.convert("RGBA")
    mask = _background_mask(rgba, op.background, op.tolerance)
    bbox = mask.getbbox()
    if bbox is None:
        return rgba
    left, top, right, bottom = bbox
    pad = op.padding
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(rgba.width, right + pad)
    bottom = min(rgba.height, bottom + pad)
    return rgba.crop((left, top, right, bottom))


def apply_trim(img: Image.Image, op: TrimOp) -> Image.Image:
    return trim_image(img, op)


def apply_flatten(img: Image.Image, op: FlattenOp) -> Image.Image:
    rgba = parse_color(op.background)
    if rgba[3] == 0:
        raise ValueError("flatten background cannot be transparent")
    base = Image.new("RGBA", img.size, rgba)
    base.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[3])
    return base


def _background_mask(img: Image.Image, background: str, tolerance: int) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()
    assert pixels is not None
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    assert mp is not None

    if background == "transparent":
        for y in range(h):
            for x in range(w):
                if pixels[x, y][3] > tolerance:
                    mp[x, y] = 255
        return mask

    target = parse_color(background)[:3]
    tol = tolerance
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a <= tolerance:
                continue
            if abs(r - target[0]) <= tol and abs(g - target[1]) <= tol and abs(b - target[2]) <= tol:
                continue
            mp[x, y] = 255
    return mask
