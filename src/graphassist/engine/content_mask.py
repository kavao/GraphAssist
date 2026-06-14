"""Content / opaque pixel masks (shared by trim and spatial metrics)."""

from __future__ import annotations

from PIL import Image

from graphassist.engine.colors import parse_color


def opaque_mask(img: Image.Image, *, alpha_threshold: int = 128) -> Image.Image:
    """Luminance/color stats: alpha > threshold."""
    rgba = img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()
    assert pixels is not None
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    assert mp is not None
    for y in range(h):
        for x in range(w):
            if pixels[x, y][3] > alpha_threshold:
                mp[x, y] = 255
    return mask


def content_mask(
    img: Image.Image,
    *,
    background: str = "transparent",
    tolerance: int = 0,
    alpha_threshold: int = 128,
) -> Image.Image:
    """Spatial L1/L2: non-background pixels (trim-compatible).

    Trim callers should pass ``alpha_threshold=tolerance`` so low-alpha fringe
    pixels are excluded the same way as the legacy trim mask.
    """
    rgba = img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()
    assert pixels is not None
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    assert mp is not None

    if background == "transparent":
        cutoff = max(tolerance, alpha_threshold)
        for y in range(h):
            for x in range(w):
                if pixels[x, y][3] > cutoff:
                    mp[x, y] = 255
        return mask

    target = parse_color(background)[:3]
    tol = tolerance
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a <= alpha_threshold:
                continue
            if abs(r - target[0]) <= tol and abs(g - target[1]) <= tol and abs(b - target[2]) <= tol:
                continue
            mp[x, y] = 255
    return mask
