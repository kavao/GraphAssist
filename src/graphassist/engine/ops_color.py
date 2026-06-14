"""ImageJob grayscale / sepia (Phase T extension)."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageOps

from graphassist.engine.tone_utils import apply_rgb_only
from graphassist.schema.ops import GrayscaleOp, SepiaOp

# Classic sepia tone matrix (RGB → RGB)
_SEPIA_MATRIX = np.array(
    [
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131],
    ],
    dtype=np.float32,
)


def apply_grayscale(img: Image.Image, op: GrayscaleOp) -> Image.Image:
    if op.mode == "luminance":

        def to_luminance(rgb: Image.Image) -> Image.Image:
            gray = ImageOps.grayscale(rgb)
            return gray.convert("RGB")

        return apply_rgb_only(img, to_luminance)
    raise ValueError(f"unsupported grayscale mode: {op.mode}")


def apply_sepia(img: Image.Image, op: SepiaOp) -> Image.Image:
    if op.strength <= 0:
        return img.convert("RGBA")
    strength = op.strength

    def to_sepia(rgb: Image.Image) -> Image.Image:
        arr = np.asarray(rgb, dtype=np.float32)
        flat = arr.reshape(-1, 3)
        toned = flat @ _SEPIA_MATRIX.T
        if strength < 1.0:
            toned = flat * (1.0 - strength) + toned * strength
        out = np.clip(toned, 0, 255).astype(np.uint8).reshape(arr.shape)
        return Image.fromarray(out, mode="RGB")

    return apply_rgb_only(img, to_sepia)
