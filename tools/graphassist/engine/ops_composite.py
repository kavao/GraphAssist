"""合成 operation。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from tools.graphassist.engine.canvas import load
from tools.graphassist.schema.paths import resolve_input
from tools.graphassist.schema.ops import CompositeOp


def _anchor_offset(base: Image.Image, overlay: Image.Image, op: CompositeOp) -> tuple[int, int]:
    if op.anchor == "center":
        return (
            op.x + (base.width - overlay.width) // 2,
            op.y + (base.height - overlay.height) // 2,
        )
    return op.x, op.y


def apply_composite(img: Image.Image, op: CompositeOp, *, root: Path) -> Image.Image:
    overlay = load(resolve_input(op.overlay, root=root, must_exist=True))
    base = img.convert("RGBA")
    x, y = _anchor_offset(base, overlay, op)
    base.paste(overlay, (x, y), overlay)
    return base
