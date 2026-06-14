"""RGBA 画像 → MosaicArt JSON。"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from PIL import Image

from graphassist.engine.canvas import load
from graphassist.schema.mosaic import DEFAULT_MAX_COLORS, MosaicArt, MosaicMeta, rgba_to_hex

SYMBOL_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def parse_grid(value: str) -> tuple[int, int]:
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"grid must be WIDTHxHEIGHT, got: {value}")
    width, height = (int(parts[0]), int(parts[1]))
    if width < 1 or height < 1:
        raise ValueError(f"grid dimensions must be positive: {value}")
    return width, height


def encode_image(
    path: Path,
    *,
    grid_width: int,
    grid_height: int,
    max_colors: int = DEFAULT_MAX_COLORS,
    transparent: str = ".",
    alpha_threshold: int = 128,
    title: str | None = None,
) -> MosaicArt:
    img = load(path)
    return encode_rgba_image(
        img,
        grid_width=grid_width,
        grid_height=grid_height,
        max_colors=max_colors,
        transparent=transparent,
        alpha_threshold=alpha_threshold,
        title=title,
        source=path.name,
    )


def encode_rgba_image(
    img: Image.Image,
    *,
    grid_width: int,
    grid_height: int,
    max_colors: int = DEFAULT_MAX_COLORS,
    transparent: str = ".",
    alpha_threshold: int = 128,
    title: str | None = None,
    source: str | None = None,
) -> MosaicArt:
    if max_colors < 1 or max_colors > 32:
        raise ValueError("max_colors must be between 1 and 32")
    if len(transparent) != 1 or transparent.isspace():
        raise ValueError("transparent must be a single non-space character")

    rgba = img.convert("RGBA").resize((grid_width, grid_height), Image.Resampling.NEAREST)
    pixels = rgba.load()
    assert pixels is not None

    mask: list[list[bool]] = []
    rgb_rows: list[list[tuple[int, int, int] | None]] = []
    opaque_pixels: list[tuple[int, int, int]] = []

    for y in range(grid_height):
        row_mask: list[bool] = []
        row_rgb: list[tuple[int, int, int] | None] = []
        for x in range(grid_width):
            r, g, b, a = pixels[x, y]
            if a <= alpha_threshold:
                row_mask.append(True)
                row_rgb.append(None)
            else:
                row_mask.append(False)
                rgb = (r, g, b)
                row_rgb.append(rgb)
                opaque_pixels.append(rgb)
        mask.append(row_mask)
        rgb_rows.append(row_rgb)

    if not opaque_pixels:
        return MosaicArt(
            version="1.0",
            width=grid_width,
            height=grid_height,
            transparent=transparent,
            palette={"X": "#000000"},
            rows=[transparent * grid_width for _ in range(grid_height)],
            meta=MosaicMeta(title=title, source=source),
        )

    color_map = _build_color_map(opaque_pixels, max_colors=max_colors)
    representatives = set(color_map.values())
    symbol_map = _assign_symbols(representatives, transparent=transparent)
    palette = {symbol_map[rep]: rgba_to_hex((*rep, 255)) for rep in representatives}

    rows: list[str] = []
    for y in range(grid_height):
        chars: list[str] = []
        for x in range(grid_width):
            if mask[y][x]:
                chars.append(transparent)
            else:
                rgb = rgb_rows[y][x]
                assert rgb is not None
                chars.append(symbol_map[color_map[rgb]])
        rows.append("".join(chars))

    return MosaicArt(
        version="1.0",
        width=grid_width,
        height=grid_height,
        transparent=transparent,
        palette=palette,
        rows=rows,
        meta=MosaicMeta(title=title, source=source),
    )


def _build_color_map(
    opaque_pixels: list[tuple[int, int, int]],
    *,
    max_colors: int,
) -> dict[tuple[int, int, int], tuple[int, int, int]]:
    counts = Counter(opaque_pixels)
    unique = list(counts.keys())
    if len(unique) <= max_colors:
        return {rgb: rgb for rgb in unique}

    quant = Image.new("RGB", (len(opaque_pixels), 1))
    quant_pixels = quant.load()
    assert quant_pixels is not None
    for index, rgb in enumerate(opaque_pixels):
        quant_pixels[index, 0] = rgb

    reduced = quant.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    palette = reduced.getpalette()
    if palette is None:
        raise RuntimeError("failed to extract palette from quantized image")

    index_counts = Counter(reduced.getdata())
    palette_rgbs: list[tuple[int, int, int]] = []
    for index in range(max_colors):
        base = index * 3
        palette_rgbs.append((palette[base], palette[base + 1], palette[base + 2]))

    ranked_indices = [idx for idx, _ in index_counts.most_common(max_colors)]
    representative = {idx: palette_rgbs[idx] for idx in ranked_indices}

    mapping: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    for rgb in unique:
        nearest = min(representative.values(), key=lambda target: _color_distance(rgb, target))
        mapping[rgb] = nearest
    return mapping


def _color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def _assign_symbols(
    colors: list[tuple[int, int, int]] | set[tuple[int, int, int]],
    *,
    transparent: str,
) -> dict[tuple[int, int, int], str]:
    symbols = [ch for ch in SYMBOL_ALPHABET if ch != transparent]
    if len(colors) > len(symbols):
        raise ValueError(f"too many colors ({len(colors)}) for available symbols")

    ranked = sorted(colors, key=lambda rgb: (rgb[0], rgb[1], rgb[2]))
    return {rgb: symbols[index] for index, rgb in enumerate(ranked)}
