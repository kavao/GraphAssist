"""ImageJob tone operations: curve, quantize, posterize (Phase T2/T4)."""

from __future__ import annotations

from PIL import Image, ImageOps

from graphassist.engine.tone_utils import apply_rgb_only, build_gamma_lut, build_levels_lut
from graphassist.schema.ops import CurveOp, PosterizeOp, QuantizeOp


def apply_curve(img: Image.Image, op: CurveOp) -> Image.Image:
    if op.mode == "gamma":
        lut = build_gamma_lut(op.gamma)
        return apply_rgb_only(img, lambda rgb: rgb.point(lut * 3))
    lut = build_levels_lut(op.black, op.white)
    return apply_rgb_only(img, lambda rgb: rgb.point(lut * 3))


def apply_quantize(img: Image.Image, op: QuantizeOp) -> Image.Image:
    rgba = img.convert("RGBA")
    r, g, b, a = rgba.split()
    rgb = Image.merge("RGB", (r, g, b))
    dither = Image.Dither.FLOYDSTEINBERG if op.dither else Image.Dither.NONE
    quantized = rgb.quantize(colors=op.colors, method=Image.Quantize.MEDIANCUT, dither=dither)
    out_rgb = quantized.convert("RGB")
    out = out_rgb.convert("RGBA")
    out.putalpha(a)
    return out


def apply_posterize(img: Image.Image, op: PosterizeOp) -> Image.Image:
    return apply_rgb_only(img, lambda rgb: ImageOps.posterize(rgb, op.bits))
