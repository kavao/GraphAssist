"""ImageJob to_mosaic operation (Phase M3)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from graphassist.engine.mosaic_encode import encode_rgba_image, parse_grid
from graphassist.engine.mosaic_export import export_json
from graphassist.schema.ops import ToMosaicOp
from graphassist.schema.paths import project_root, resolve_mosaic_output


def apply_to_mosaic(img: Image.Image, op: ToMosaicOp, *, root: Path | None = None) -> Image.Image:
    base = root or project_root()
    grid_w, grid_h = parse_grid(op.grid)
    art = encode_rgba_image(
        img,
        grid_width=grid_w,
        grid_height=grid_h,
        max_colors=op.max_colors,
        transparent=op.transparent,
        alpha_threshold=op.alpha_threshold,
        title=op.title,
        source=op.title or "imagejob",
    )
    out_path = resolve_mosaic_output(op.mosaic_output, root=base)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(export_json(art), encoding="utf-8")
    return img
