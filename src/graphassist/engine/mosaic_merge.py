"""MosaicArt 合成（blit / palette remap / trunk preset）。"""

from __future__ import annotations

import string
from dataclasses import dataclass, field

from graphassist.schema.mosaic import MAX_PALETTE_SIZE, MosaicArt, MosaicMeta

TRUNK_PALETTE: dict[str, str] = {
    "H": "#8D6E63",
    "h": "#5D4037",
    "D": "#A1887F",
    "E": "#4E342E",
    "n": "#689F38",
}

PARAKEET_TO_BIRDS: dict[str, str] = {
    "Y": "1",
    "G": "2",
    "g": "3",
    "B": "4",
    "b": "5",
    "O": "o",
    "K": "K",
    "W": "7",
    "L": "6",
}

PARROT_TO_BIRDS: dict[str, str] = {
    "O": "P",
}

BIRDS_CANVAS = (50, 26)
BIRDS_PARAKEET_OFFSET = (8, 6)
BIRDS_PARROT_OFFSET = (24, 3)
BIRDS_TRUNK_TOP_ROW = 19

# 正本 birds_on_trunk.json の幹・枝行（width=50）
BIRDS_TRUNK_ROW_TEMPLATES: tuple[str, ...] = (
    "...EHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHE...",
    "...EhhDhhDhhDhhDhhDhhDhhDhhDhhDhhDhhDhhDhhDhhDE...",
    "...............33......hHh......RR................",
    ".......................hHh........................",
    "......................hDHDh.......................",
    ".....................hDhHhDh......................",
    "....................EDhDHDhDE.....................",
)

# 幹テンプレ行に現れる鳥パレット文字（blit 後に上書きされる箇所）
BIRDS_TEMPLATE_EXTRA_PALETTE: dict[str, str] = {
    "1": "#F9E547",
    "3": "#3D8B37",
    "R": "#E53935",
    "r": "#C62828",
}


@dataclass
class MergeLayer:
    art: MosaicArt
    x: int = 0
    y: int = 0
    key_map: dict[str, str] | None = None
    colors: dict[str, str] = field(default_factory=dict)


def merge_mosaics(
    *,
    width: int,
    height: int,
    layers: list[MergeLayer],
    transparent: str = ".",
    title: str | None = None,
    description: str | None = None,
) -> MosaicArt:
    grid = [[transparent] * width for _ in range(height)]
    palette: dict[str, str] = {}

    for layer in layers:
        char_map = _resolve_char_map(layer, palette, transparent)
        _blit_layer(grid, layer.art, layer.x, layer.y, char_map, transparent, width, height)

    if len(palette) > MAX_PALETTE_SIZE:
        raise ValueError(f"merged palette exceeds {MAX_PALETTE_SIZE} colors ({len(palette)})")

    rows = ["".join(row) for row in grid]
    meta = MosaicMeta(title=title, source="merge", description=description)
    art = MosaicArt(
        version="1.0",
        width=width,
        height=height,
        transparent=transparent,
        palette=palette,
        rows=rows,
        meta=meta,
    )
    return art


def add_branch_trunk(
    width: int,
    height: int,
    *,
    trunk_top_row: int,
    branch_row: int | None = None,
    branch_cx: int | None = None,
    transparent: str = ".",
    row_templates: tuple[str, ...] | None = None,
    extra_palette: dict[str, str] | None = None,
) -> MosaicArt:
    """幹＋根元の CharGrid 断片（鳥は別 layer で blit）。"""
    grid = [[transparent] * width for _ in range(height)]
    palette = dict(TRUNK_PALETTE)
    if extra_palette:
        palette.update(extra_palette)

    if row_templates:
        for index, template in enumerate(row_templates):
            y = trunk_top_row + index
            if y >= height:
                break
            if len(template) != width:
                raise ValueError(f"trunk template row {index} width {len(template)} != canvas {width}")
            for x, ch in enumerate(template):
                if ch == transparent:
                    continue
                if ch not in palette:
                    raise ValueError(f"unknown trunk char {ch!r} in template row {index}")
                grid[y][x] = ch
    else:
        if trunk_top_row < height:
            _paint_trunk_bar(grid, trunk_top_row, width)
        if trunk_top_row + 1 < height:
            _paint_trunk_texture(grid, trunk_top_row + 1, width)
        if branch_row is not None and branch_cx is not None and branch_row < height:
            _paint_branch(grid, branch_row, branch_cx, width)

    rows = ["".join(row) for row in grid]
    return MosaicArt(
        version="1.0",
        width=width,
        height=height,
        transparent=transparent,
        palette=palette,
        rows=rows,
        meta=MosaicMeta(title="trunk", source="merge"),
    )


def compose_birds_on_trunk(parakeet: MosaicArt, parrot: MosaicArt) -> MosaicArt:
    """parakeet + parrot + trunk preset → birds_on_trunk 相当（50×26）。"""
    width, height = BIRDS_CANVAS
    trunk = add_branch_trunk(
        width,
        height,
        trunk_top_row=BIRDS_TRUNK_TOP_ROW,
        row_templates=BIRDS_TRUNK_ROW_TEMPLATES,
        extra_palette=BIRDS_TEMPLATE_EXTRA_PALETTE,
    )
    parakeet_layer = MergeLayer(
        parakeet,
        x=BIRDS_PARAKEET_OFFSET[0],
        y=BIRDS_PARAKEET_OFFSET[1],
        key_map=dict(PARAKEET_TO_BIRDS),
        colors={"K": "#212121"},
    )
    parrot_layer = MergeLayer(
        parrot,
        x=BIRDS_PARROT_OFFSET[0],
        y=BIRDS_PARROT_OFFSET[1],
        key_map=dict(PARROT_TO_BIRDS),
    )
    return merge_mosaics(
        width=width,
        height=height,
        layers=[MergeLayer(trunk), parakeet_layer, parrot_layer],
        title="birds_on_trunk",
        description="インコとオウムが木の幹の上で仲良く並ぶ",
    )


def _resolve_char_map(layer: MergeLayer, palette: dict[str, str], transparent: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for key, color in layer.art.palette.items():
        desired = layer.key_map.get(key, key) if layer.key_map else key
        resolved_color = layer.colors.get(key) or layer.colors.get(desired) or color

        dest = desired
        if dest in palette:
            if palette[dest].lower() == resolved_color.lower():
                mapping[key] = dest
                continue
            dest = _allocate_key(palette, transparent, preferred=None)
        palette[dest] = resolved_color
        mapping[key] = dest
    return mapping


def _allocate_key(palette: dict[str, str], transparent: str, *, preferred: str | None) -> str:
    if preferred and preferred not in palette and preferred != transparent:
        return preferred
    used = set(palette) | {transparent}
    for candidate in _iter_key_candidates():
        if candidate not in used:
            return candidate
    raise ValueError("no available palette key characters")


def _iter_key_candidates():
    for ch in string.digits:
        yield ch
    for ch in string.ascii_letters:
        yield ch
    for ch in string.punctuation:
        if ch.isprintable() and not ch.isspace():
            yield ch


def _blit_layer(
    grid: list[list[str]],
    art: MosaicArt,
    x: int,
    y: int,
    char_map: dict[str, str],
    transparent: str,
    canvas_w: int,
    canvas_h: int,
) -> None:
    for dy, row in enumerate(art.rows):
        cy = y + dy
        if cy < 0 or cy >= canvas_h:
            continue
        for dx, ch in enumerate(row):
            if ch == art.transparent:
                continue
            cx = x + dx
            if cx < 0 or cx >= canvas_w:
                continue
            mapped = char_map.get(ch, ch)
            if mapped == transparent:
                continue
            grid[cy][cx] = mapped


def _paint_trunk_bar(grid: list[list[str]], y: int, width: int) -> None:
    for x in range(width):
        if x < 3 or x >= width - 3:
            continue
        if x in (3, width - 4):
            grid[y][x] = "E"
        else:
            grid[y][x] = "H"


def _paint_trunk_texture(grid: list[list[str]], y: int, width: int) -> None:
    pattern = ("h", "h", "D")
    for idx, x in enumerate(range(4, width - 4)):
        grid[y][x] = pattern[idx % len(pattern)]
    if width >= 8:
        grid[y][3] = "E"
        grid[y][width - 4] = "E"


def _paint_branch(grid: list[list[str]], y: int, cx: int, width: int) -> None:
    if 0 <= cx - 1 < width:
        grid[y][cx - 1] = "h"
    if 0 <= cx < width:
        grid[y][cx] = "H"
    if 0 <= cx + 1 < width:
        grid[y][cx + 1] = "h"
    if y + 1 < len(grid) and 0 <= cx < width:
        grid[y + 1][cx] = "h"
    if y + 2 < len(grid):
        for dx, ch in enumerate("hDh"):
            x = cx - 1 + dx
            if 0 <= x < width:
                grid[y + 2][x] = ch
    if y + 3 < len(grid):
        for dx, ch in enumerate("EDh"):
            x = cx - 2 + dx
            if 0 <= x < width:
                grid[y + 3][x] = ch
        if 0 <= cx + 2 < width:
            grid[y + 3][cx + 2] = "D"
        if 0 <= cx + 3 < width:
            grid[y + 3][cx + 3] = "h"
        if 0 <= cx + 4 < width:
            grid[y + 3][cx + 4] = "D"
        if 0 <= cx + 5 < width:
            grid[y + 3][cx + 5] = "h"
        if 0 <= cx + 6 < width:
            grid[y + 3][cx + 6] = "E"
