"""RGB-only image transforms while preserving alpha (Phase T)."""

from __future__ import annotations

from collections.abc import Callable

from PIL import Image


def apply_rgb_only(img: Image.Image, fn: Callable[[Image.Image], Image.Image]) -> Image.Image:
    rgba = img.convert("RGBA")
    r, g, b, a = rgba.split()
    rgb = Image.merge("RGB", (r, g, b))
    processed = fn(rgb)
    r2, g2, b2 = processed.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def build_gamma_lut(gamma: float) -> list[int]:
    return [min(255, int((i / 255.0) ** gamma * 255 + 0.5)) for i in range(256)]


def build_levels_lut(black: int, white: int) -> list[int]:
    span = white - black

    def map_value(value: int) -> int:
        if value <= black:
            return 0
        if value >= white:
            return 255
        return int((value - black) / span * 255 + 0.5)

    return [map_value(i) for i in range(256)]
