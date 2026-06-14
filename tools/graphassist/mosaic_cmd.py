"""mosaic サブコマンド（encode / decode / export）。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from tools.graphassist.engine.canvas import save
from tools.graphassist.engine.mosaic_decode import render_mosaic
from tools.graphassist.engine.mosaic_encode import encode_image, parse_grid
from tools.graphassist.engine.mosaic_export import export_js, export_json
from tools.graphassist.schema.mosaic import MosaicArt
from tools.graphassist.schema.paths import (
    project_root,
    resolve_input,
    resolve_mosaic_json,
    resolve_mosaic_output,
    resolve_output,
)


@dataclass
class MosaicDecodeOptions:
    cell_size: int = 1
    fmt: str = "png"
    quality: int = 85


@dataclass
class MosaicEncodeOptions:
    grid: str
    max_colors: int = 16
    transparent: str = "."
    alpha_threshold: int = 128


def load_mosaic_json(path: Path, *, root: Path | None = None) -> MosaicArt:
    base = root or project_root()
    rel = _relative_path(path, base)
    resolved = resolve_mosaic_json(rel, root=base, must_exist=True)
    data = json.loads(resolved.read_text(encoding="utf-8"))
    return MosaicArt.model_validate(data)


def run_decode(
    json_path: Path,
    output_path: Path,
    opts: MosaicDecodeOptions,
    *,
    root: Path | None = None,
) -> Path:
    base = root or project_root()
    art = load_mosaic_json(json_path, root=base)
    return run_decode_art(art, output_path, opts, root=base)


def run_decode_art(
    art: MosaicArt,
    output_path: Path,
    opts: MosaicDecodeOptions,
    *,
    root: Path | None = None,
) -> Path:
    base = root or project_root()
    rel_out = _relative_path(output_path, base)
    out = resolve_output(rel_out, root=base)
    img = render_mosaic(art, cell_size=opts.cell_size)
    save(img, out, fmt=opts.fmt, quality=opts.quality)
    return out


def run_encode(
    input_path: Path,
    output_path: Path,
    opts: MosaicEncodeOptions,
    *,
    root: Path | None = None,
) -> Path:
    base = root or project_root()
    rel_in = _relative_path(input_path, base)
    rel_out = _relative_path(output_path, base)
    src = resolve_input(rel_in, root=base, must_exist=True)
    out = resolve_mosaic_output(rel_out, root=base)
    grid_w, grid_h = parse_grid(opts.grid)
    art = encode_image(
        src,
        grid_width=grid_w,
        grid_height=grid_h,
        max_colors=opts.max_colors,
        transparent=opts.transparent,
        alpha_threshold=opts.alpha_threshold,
        title=src.stem,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(export_json(art), encoding="utf-8")
    return out


def run_export(
    json_path: Path,
    *,
    fmt: str = "js",
    output_path: Path | None = None,
    name: str | None = None,
    root: Path | None = None,
) -> str:
    base = root or project_root()
    rel_json = _relative_path(json_path, base)
    art = load_mosaic_json(Path(rel_json), root=base)
    if fmt == "js":
        text = export_js(art, name=name)
    elif fmt == "json":
        text = export_json(art)
    else:
        raise ValueError(f"unsupported export format: {fmt}")

    if output_path is not None:
        rel_out = _relative_path(output_path, base)
        out = resolve_mosaic_output(rel_out, root=base)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return text


def _relative_path(path: Path, base: Path) -> str:
    if path.is_absolute():
        return str(path.relative_to(base))
    return str(path).replace("\\", "/")
