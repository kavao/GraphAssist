"""LineArt CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

from graphassist.engine.lineart.rasterize import rasterize_lineart_svg
from graphassist.engine.lineart.svg_export import write_svg
from graphassist.schema.lineart import LineArtDocument
from graphassist.schema.paths import resolve_lineart_input, resolve_lineart_output, resolve_lineart_raster_output


def load_lineart_document(path: Path) -> LineArtDocument:
    return LineArtDocument.model_validate(json.loads(path.read_text(encoding="utf-8")))


def run_lineart_render(
    json_path: Path,
    output: Path,
    *,
    root: Path | None = None,
    dry_run: bool = False,
    png_output: Path | None = None,
    png_width: int | None = None,
) -> Path:
    if png_width is not None and png_width <= 0:
        raise ValueError("png_width must be greater than 0")
    input_path = resolve_lineart_input(str(json_path), root=root, must_exist=True)
    output_path = resolve_lineart_output(str(output), root=root)
    png_path = resolve_lineart_raster_output(str(png_output), root=root) if png_output is not None else None
    document = load_lineart_document(input_path)
    if dry_run:
        return output_path
    svg_path = write_svg(document, output_path)
    if png_path is not None:
        rasterize_lineart_svg(svg_path, png_path, width=png_width or document.canvas.width)
    return svg_path
