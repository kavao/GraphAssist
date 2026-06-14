"""ImageJob adjust operation (Phase T1)."""

from __future__ import annotations

from PIL import Image, ImageEnhance

from graphassist.schema.ops import AdjustOp


def apply_adjust(img: Image.Image, op: AdjustOp) -> Image.Image:
    rgba = img.convert("RGBA")
    rgb = rgba.convert("RGB")
    if op.brightness != 1.0:
        rgb = ImageEnhance.Brightness(rgb).enhance(op.brightness)
    if op.contrast != 1.0:
        rgb = ImageEnhance.Contrast(rgb).enhance(op.contrast)
    if op.saturation != 1.0:
        rgb = ImageEnhance.Color(rgb).enhance(op.saturation)
    out = rgb.convert("RGBA")
    out.putalpha(rgba.split()[3])
    return out
