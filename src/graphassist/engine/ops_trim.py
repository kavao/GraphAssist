"""トリミング・flatten。"""

from __future__ import annotations

from PIL import Image

from graphassist.engine.content_mask import content_mask
from graphassist.engine.colors import parse_color
from graphassist.schema.ops import FlattenOp, TrimOp


def trim_image(img: Image.Image, op: TrimOp) -> Image.Image:
    rgba = img.convert("RGBA")
    mask = content_mask(rgba, background=op.background, tolerance=op.tolerance, alpha_threshold=op.tolerance)
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
