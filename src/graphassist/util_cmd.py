"""trim / diff / inspect / sheet / palette CLI。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from graphassist.convert_cmd import collect_inputs
from graphassist.engine.canvas import load, save
from graphassist.engine.diff import diff_images
from graphassist.engine.inspect import inspect_image, inspect_many
from graphassist.engine.palette import extract_palette
from graphassist.engine.ops_trim import trim_image
from graphassist.engine.sheet import contact_sheet, sheet_pack, sheet_split
from graphassist.schema.ops import TrimOp


@dataclass
class TrimOptions:
    background: str = "transparent"
    padding: int = 0
    tolerance: int = 0


def run_trim(input_path: Path, output_path: Path, opts: TrimOptions) -> list[Path]:
    op = TrimOp(
        type="trim",
        background=opts.background,  # type: ignore[arg-type]
        padding=opts.padding,
        tolerance=opts.tolerance,
    )
    inputs = collect_inputs(input_path)
    input_is_dir = input_path.is_dir()
    if input_is_dir:
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for index, src in enumerate(inputs, start=1):
        img = trim_image(load(src), op)
        if input_is_dir or not output_path.suffix:
            dst = output_path / f"{src.stem}.png" if input_is_dir else Path(str(output_path) + ".png")
        else:
            dst = output_path
        save(img, dst, fmt="png")
        created.append(dst)
    return created


def run_diff(before: Path, after: Path, output: Path, *, threshold: int = 16) -> tuple[Path, dict]:
    img, meta = diff_images(load(before), load(after), threshold=threshold)
    output.parent.mkdir(parents=True, exist_ok=True)
    save(img, output, fmt="png")
    return output, meta


def run_inspect(
    input_path: Path,
    *,
    fmt: str = "text",
    max_long_edge: int | None = None,
) -> str:
    if input_path.is_dir():
        paths = collect_inputs(input_path)
        rows = inspect_many(paths, max_long_edge=max_long_edge)
    else:
        rows = [inspect_image(input_path, max_long_edge=max_long_edge)]
    if fmt == "json":
        return json.dumps(rows if len(rows) > 1 else rows[0], ensure_ascii=False, indent=2) + "\n"
    lines = []
    for row in rows:
        if row.get("ok"):
            lines.append(
                f"{row['path']}: {row['width']}x{row['height']} {row['mode']} alpha={row['has_alpha']}"
            )
        else:
            lines.append(f"{row['path']}: ERROR {row.get('error', 'unknown')}")
    return "\n".join(lines) + "\n"


def run_contact_sheet(
    input_path: Path,
    output: Path,
    *,
    cols: int | None,
    thumb: int,
    padding: int,
) -> Path:
    inputs = collect_inputs(input_path)
    return contact_sheet(inputs, output, cols=cols, thumb_width=thumb, padding=padding)


def run_sheet_pack(
    input_path: Path,
    output: Path,
    *,
    cell_width: int,
    cell_height: int,
    cols: int,
    padding: int,
) -> Path:
    inputs = collect_inputs(input_path)
    return sheet_pack(inputs, output, cell_width=cell_width, cell_height=cell_height, cols=cols, padding=padding)


def run_sheet_split(
    input_path: Path,
    output_dir: Path,
    *,
    cell_width: int,
    cell_height: int,
    cols: int,
    rows: int,
    padding: int,
) -> list[Path]:
    return sheet_split(
        input_path,
        output_dir,
        cell_width=cell_width,
        cell_height=cell_height,
        cols=cols,
        rows=rows,
        padding=padding,
    )


def run_palette(input_path: Path, *, max_colors: int = 16, fmt: str = "json") -> str:
    img = load(input_path)
    colors = extract_palette(img, max_colors=max_colors)
    if fmt == "json":
        return json.dumps({"colors": colors}, ensure_ascii=False, indent=2) + "\n"
    return "\n".join(f"{c['hex']} {c['ratio']}" for c in colors) + "\n"
