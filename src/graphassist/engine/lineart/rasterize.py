"""LineArt SVG rasterization helpers."""

from __future__ import annotations

from pathlib import Path

from graphassist.engine.catalog_fetch import rasterize_svg


def rasterize_lineart_svg(svg_path: Path, png_path: Path, *, width: int) -> Path:
    try:
        rasterize_svg(svg_path, png_path, width=width)
    except RuntimeError as exc:
        message = str(exc).replace("catalog SVG", "LineArt SVG")
        raise RuntimeError(message) from exc
    return png_path
