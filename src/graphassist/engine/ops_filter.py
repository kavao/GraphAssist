"""ImageJob blur / sharpen operations (Phase T3)."""

from __future__ import annotations

from PIL import Image, ImageEnhance, ImageFilter

from graphassist.engine.tone_utils import apply_rgb_only
from graphassist.schema.ops import BlurOp, SharpenOp


def apply_blur(img: Image.Image, op: BlurOp) -> Image.Image:
    if op.radius <= 0:
        return img.convert("RGBA")

    def blur_rgb(rgb: Image.Image) -> Image.Image:
        if op.kind == "box":
            radius = max(1, int(round(op.radius)))
            return rgb.filter(ImageFilter.BoxBlur(radius))
        return rgb.filter(ImageFilter.GaussianBlur(radius=op.radius))

    return apply_rgb_only(img, blur_rgb)


def apply_sharpen(img: Image.Image, op: SharpenOp) -> Image.Image:
    if op.kind == "unsharp":
        return apply_rgb_only(
            img,
            lambda rgb: rgb.filter(
                ImageFilter.UnsharpMask(
                    radius=op.radius,
                    percent=op.percent,
                    threshold=op.threshold,
                )
            ),
        )
    if op.amount == 1.0:
        return img.convert("RGBA")
    return apply_rgb_only(img, lambda rgb: ImageEnhance.Sharpness(rgb).enhance(op.amount))
