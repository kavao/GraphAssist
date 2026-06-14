"""幾何変換 operation。"""

from __future__ import annotations

from PIL import Image, ImageOps

from graphassist.engine.colors import parse_color
from graphassist.engine.canvas import resize_long_edge, resize_wh
from graphassist.schema.ops import BorderOp, CropOp, ExtendOp, ResizeOp, RotateOp


def apply_resize(img: Image.Image, op: ResizeOp) -> Image.Image:
    if op.long_edge is not None:
        return resize_long_edge(img, op.long_edge)
    if op.width is not None or op.height is not None:
        return resize_wh(img, op.width, op.height)
    raise ValueError("resize requires width, height, or long_edge")


def apply_crop(img: Image.Image, op: CropOp) -> Image.Image:
    w, h = img.size
    if op.x + op.width > w or op.y + op.height > h:
        raise ValueError(f"crop exceeds image bounds: {w}x{h}")
    return img.crop((op.x, op.y, op.x + op.width, op.y + op.height))


def apply_extend(img: Image.Image, op: ExtendOp) -> Image.Image:
    w, h = img.size
    new_w = w + op.left + op.right
    new_h = h + op.top + op.bottom
    canvas = Image.new("RGBA", (new_w, new_h), parse_color(op.fill))
    canvas.paste(img, (op.left, op.top), img if img.mode == "RGBA" else None)
    return canvas


def apply_rotate(img: Image.Image, op: RotateOp) -> Image.Image:
    fill = parse_color(op.fill)
    return img.rotate(op.degrees, expand=True, resample=Image.Resampling.BICUBIC, fillcolor=fill)


def apply_border(img: Image.Image, op: BorderOp) -> Image.Image:
    rgba = parse_color(op.color)
    if rgba[3] == 0:
        # transparent border via manual extend
        return apply_extend(
            img,
            ExtendOp(type="extend", left=op.size, right=op.size, top=op.size, bottom=op.size, fill=op.color),
        )
    rgb = rgba[:3]
    return ImageOps.expand(img.convert("RGBA"), border=op.size, fill=rgb + (255,))
