"""analyze CLI (Phase A + L)."""

from __future__ import annotations

import json
from pathlib import Path

from graphassist.engine.canvas import is_image_path
from graphassist.engine.metrics import MetricsOptions, analyze_image, analyze_many, compare_images


def _parse_roi(value: str) -> dict:
    parts = value.split(",")
    if len(parts) != 5:
        raise ValueError(f"roi must be name,x,y,width,height: {value}")
    name, x, y, w, h = parts[0].strip(), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
    return {"name": name, "x": x, "y": y, "width": w, "height": h}


def _format_text_profile(data: dict) -> str:
    if not data.get("ok", True):
        return f"error: {data.get('error', 'unknown')}\n"
    lum = data.get("luminance", {})
    line = f"{data.get('path')}: luminance_mean={lum.get('mean')} opaque_ratio={data.get('structure', {}).get('opaque_ratio')}"
    if "spatial" in data:
        bbox = data["spatial"].get("content_bbox")
        if bbox:
            line += f" bbox=({bbox['x']},{bbox['y']},{bbox['width']}x{bbox['height']})"
    return line + "\n"


def _format_text_compare(data: dict) -> str:
    if not data.get("ok", True):
        return f"error: {data.get('error', 'unknown')}\n"
    v = data.get("verdict", {})
    d = data.get("delta", {})
    return (
        f"compare {data.get('a')} vs {data.get('b')}: "
        f"brightness_relation={v.get('brightness_relation')} "
        f"delta_luminance={d.get('luminance_mean')}\n"
    )


def run_analyze(
    input_path: Path,
    *,
    compare: Path | None = None,
    fmt: str = "json",
    output: Path | None = None,
    max_long_edge: int = 512,
    max_colors: int = 8,
    alpha_threshold: int = 128,
    threshold_brightness: float = 0.15,
    threshold_palette: float = 0.30,
    full_profiles: bool = False,
    spatial: bool = False,
    background: str = "transparent",
    tolerance: int = 0,
    grid_rows: int = 3,
    grid_cols: int = 3,
    rois: list[str] | None = None,
    root: Path | None = None,
) -> str:
    opts = MetricsOptions(
        max_long_edge=max_long_edge,
        max_colors=max_colors,
        alpha_threshold=alpha_threshold,
        threshold_brightness=threshold_brightness,
        threshold_palette=threshold_palette,
        full_profiles=full_profiles,
        spatial=spatial,
        background=background,
        tolerance=tolerance,
        grid_rows=grid_rows,
        grid_cols=grid_cols,
        rois=[_parse_roi(r) for r in rois] if rois else None,
    )

    if compare is not None:
        data = compare_images(input_path, compare, opts=opts)
    elif input_path.is_dir():
        paths = sorted(p for p in input_path.iterdir() if p.is_file() and is_image_path(p))
        data = analyze_many(paths, opts=opts)
    else:
        data = analyze_image(input_path, opts=opts)

    if fmt == "text":
        if data.get("kind") == "compare":
            text = _format_text_compare(data)
        elif data.get("kind") == "profiles":
            text = "".join(_format_text_profile(item) for item in data.get("items", []))
        else:
            text = _format_text_profile(data)
    else:
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    if output is not None:
        out = output if output.is_absolute() else (root or Path.cwd()) / output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")

    return text
