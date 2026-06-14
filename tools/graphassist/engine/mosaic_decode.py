"""MosaicArt JSON → RGBA 画像。"""

from __future__ import annotations

from PIL import Image

from tools.graphassist.schema.mosaic import MosaicArt, parse_hex_color


def render_mosaic(art: MosaicArt, *, cell_size: int = 1) -> Image.Image:
    if cell_size < 1:
        raise ValueError("cell_size must be >= 1")

    palette_rgba = {key: parse_hex_color(value) for key, value in art.palette.items()}
    img = Image.new("RGBA", (art.width, art.height), (0, 0, 0, 0))
    pixels = img.load()
    assert pixels is not None

    for y, row in enumerate(art.rows):
        for x, char in enumerate(row):
            if char == art.transparent:
                continue
            pixels[x, y] = palette_rgba[char]

    if cell_size == 1:
        return img
    return img.resize(
        (art.width * cell_size, art.height * cell_size),
        Image.Resampling.NEAREST,
    )
