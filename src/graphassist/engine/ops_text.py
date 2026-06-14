"""テキスト描画 operation。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from graphassist.engine.colors import parse_color
from graphassist.schema.ops import TextOp
from graphassist.schema.paths import resolve_font


def apply_text(img: Image.Image, op: TextOp, *, root: Path) -> Image.Image:
    if op.direction == "vertical":
        return _apply_text_vertical(img, op, root=root)
    return _apply_text_horizontal(img, op, root=root)


def _apply_text_horizontal(img: Image.Image, op: TextOp, *, root: Path) -> Image.Image:
    working = img.convert("RGBA")
    font = _load_font(op, root=root)
    draw = ImageDraw.Draw(working)
    stroke_width, stroke_fill = _stroke(op)
    draw.text(
        (op.x, op.y),
        op.content,
        font=font,
        fill=parse_color(op.color),
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )
    return working


def _apply_text_vertical(img: Image.Image, op: TextOp, *, root: Path) -> Image.Image:
    working = img.convert("RGBA")
    font = _load_font(op, root=root)
    draw = ImageDraw.Draw(working)
    stroke_width, stroke_fill = _stroke(op)
    fill = parse_color(op.color)
    x, y = op.x, op.y
    gap = max(1, int(op.size * (op.line_spacing - 1.0)))
    for char in op.content:
        if char == "\n":
            continue
        draw.text(
            (x, y),
            char,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        bbox = draw.textbbox((x, y), char, font=font, stroke_width=stroke_width)
        y = bbox[3] + gap
    return working


def _load_font(op: TextOp, *, root: Path) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = resolve_font(op.font, root=root, must_exist=True)
    return ImageFont.truetype(str(font_path), op.size)


def _stroke(op: TextOp) -> tuple[int, tuple[int, int, int, int] | None]:
    stroke_width = op.stroke_width if op.stroke_color else 0
    stroke_fill = parse_color(op.stroke_color) if op.stroke_color else None
    return stroke_width, stroke_fill
