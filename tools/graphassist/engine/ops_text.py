"""テキスト描画 operation。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from tools.graphassist.engine.colors import parse_color
from tools.graphassist.schema.ops import TextOp
from tools.graphassist.schema.paths import resolve_font


def apply_text(img: Image.Image, op: TextOp, *, root: Path) -> Image.Image:
    working = img.convert("RGBA")
    font_path = resolve_font(op.font, root=root, must_exist=True)
    font = ImageFont.truetype(str(font_path), op.size)
    draw = ImageDraw.Draw(working)
    stroke_width = op.stroke_width if op.stroke_color else 0
    stroke_fill = parse_color(op.stroke_color) if op.stroke_color else None
    draw.text(
        (op.x, op.y),
        op.content,
        font=font,
        fill=parse_color(op.color),
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )
    return working
