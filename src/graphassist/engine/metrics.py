"""Image metrics: profile and compare (Phase A)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from graphassist.engine.canvas import is_image_path, load, resize_long_edge
from graphassist.engine.content_mask import opaque_mask
from graphassist.engine.diff import diff_images
from graphassist.engine.inspect import inspect_image
from graphassist.engine.palette import extract_palette
from graphassist.engine.spatial_metrics import AnalyzeOptions, analyze_spatial, compare_spatial


@dataclass(frozen=True)
class MetricsOptions:
    max_long_edge: int = 512
    max_colors: int = 8
    alpha_threshold: int = 128
    threshold_brightness: float = 0.15
    threshold_palette: float = 0.30
    pixel_unchanged: float = 0.01
    spatial: bool = False
    background: str = "transparent"
    tolerance: int = 0
    grid_rows: int = 3
    grid_cols: int = 3
    rois: list[dict] | None = None
    full_profiles: bool = False


def _prepare_rgba(path: Path, opts: MetricsOptions) -> tuple[Image.Image, Image.Image]:
    img = load(path)
    if opts.max_long_edge > 0:
        img = resize_long_edge(img, opts.max_long_edge)
    mask = opaque_mask(img, alpha_threshold=opts.alpha_threshold)
    return img, mask


def _luminance_array(rgba: Image.Image, mask: Image.Image) -> np.ndarray:
    arr = np.array(rgba, dtype=np.float32)
    m = np.array(mask, dtype=bool)
    if not m.any():
        return np.array([], dtype=np.float32)
    rgb = arr[m, :3]
    y = (0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2]) / 255.0
    return y.astype(np.float32)


def _round_float(value: float, places: int = 4) -> float:
    return round(float(value), places)


def _luminance_stats(y: np.ndarray) -> dict | None:
    if y.size == 0:
        return None
    return {
        "space": "rec601_relative_0_1",
        "mean": _round_float(y.mean()),
        "std": _round_float(y.std()),
        "min": _round_float(y.min()),
        "max": _round_float(y.max()),
        "p05": _round_float(np.percentile(y, 5)),
        "p50": _round_float(np.percentile(y, 50)),
        "p95": _round_float(np.percentile(y, 95)),
    }


def _color_stats(rgba: Image.Image, mask: Image.Image, *, max_colors: int) -> dict | None:
    m = np.array(mask, dtype=bool)
    if not m.any():
        return None
    arr = np.array(rgba, dtype=np.float32)
    rgb = arr[m, :3]
    mean_rgb = [int(round(v)) for v in rgb.mean(axis=0)]
    hsv = rgba.convert("HSV")
    s = np.array(hsv, dtype=np.float32)[m, 1] / 255.0
    palette = extract_palette(rgba, max_colors=max_colors)
    for entry in palette:
        entry.pop("count", None)
    return {
        "mean_rgb": mean_rgb,
        "saturation_mean": _round_float(s.mean()),
        "palette": palette,
    }


def _contrast_stats(y: np.ndarray) -> dict | None:
    if y.size == 0:
        return None
    y_min = float(y.min())
    y_max = float(y.max())
    denom = y_max + y_min + 1e-6
    return {
        "rms": _round_float(y.std()),
        "michelson": _round_float((y_max - y_min) / denom),
    }


def _structure_block(path: Path, rgba: Image.Image, mask: Image.Image) -> dict:
    inspected = inspect_image(path)
    m = np.array(mask, dtype=bool)
    opaque_ratio = _round_float(m.sum() / m.size if m.size else 0.0)
    return {
        "width": rgba.width,
        "height": rgba.height,
        "mode": "RGBA",
        "has_alpha": True,
        "opaque_ratio": opaque_ratio,
        "format": inspected.get("format"),
    }


def _sample_block(rgba: Image.Image, mask: Image.Image, opts: MetricsOptions) -> dict:
    m = np.array(mask, dtype=bool)
    return {
        "max_long_edge": opts.max_long_edge,
        "sampled_pixels": int(m.sum()),
        "alpha_threshold": opts.alpha_threshold,
    }


def analyze_image(path: Path, *, opts: MetricsOptions | None = None) -> dict:
    opts = opts or MetricsOptions()
    path = path.resolve()
    result: dict = {"version": "1.0", "kind": "profile", "path": str(path), "ok": True}

    if not path.is_file():
        return {**result, "ok": False, "error": f"file not found: {path}"}
    if not is_image_path(path):
        return {**result, "ok": False, "error": f"not an image: {path}"}

    rgba, mask = _prepare_rgba(path, opts)
    y = _luminance_array(rgba, mask)
    if y.size == 0:
        return {**result, "ok": False, "error": "no opaque pixels"}

    lum = _luminance_stats(y)
    assert lum is not None
    result["structure"] = _structure_block(path, rgba, mask)
    result["luminance"] = lum
    color = _color_stats(rgba, mask, max_colors=opts.max_colors)
    if color:
        result["color"] = color
    contrast = _contrast_stats(y)
    if contrast:
        result["contrast"] = contrast
    result["sample"] = _sample_block(rgba, mask, opts)

    if opts.spatial:
        spatial_opts = AnalyzeOptions(
            background=opts.background,
            tolerance=opts.tolerance,
            alpha_threshold=opts.alpha_threshold,
            grid_rows=opts.grid_rows,
            grid_cols=opts.grid_cols,
            rois=opts.rois,
        )
        result["spatial"] = analyze_spatial(rgba, spatial_opts)

    return result


def _palette_overlap(profile_a: dict, profile_b: dict, *, threshold_rgb: float = 32.0) -> float:
    pal_a = profile_a.get("color", {}).get("palette", [])
    pal_b = profile_b.get("color", {}).get("palette", [])
    if not pal_a or not pal_b:
        return 0.0
    matches = 0
    for ea in pal_a:
        ra = ea["rgba"][:3]
        for eb in pal_b:
            rb = eb["rgba"][:3]
            dist = sum((a - b) ** 2 for a, b in zip(ra, rb, strict=True)) ** 0.5
            if dist < threshold_rgb:
                matches += 1
                break
    return _round_float(matches / max(len(pal_a), 1))


def _brightness_relation(delta: float, threshold: float) -> str:
    if abs(delta) < threshold:
        return "similar"
    if delta > threshold:
        return "b_brighter_than_a"
    return "b_darker_than_a"


def compare_images(path_a: Path, path_b: Path, *, opts: MetricsOptions | None = None) -> dict:
    opts = opts or MetricsOptions()
    profile_a = analyze_image(path_a, opts=opts)
    profile_b = analyze_image(path_b, opts=opts)

    result: dict = {
        "version": "1.0",
        "kind": "compare",
        "a": str(path_a.resolve()),
        "b": str(path_b.resolve()),
        "ok": profile_a.get("ok", False) and profile_b.get("ok", False),
    }

    if not result["ok"]:
        errors = []
        if not profile_a.get("ok"):
            errors.append(profile_a.get("error", "profile_a failed"))
        if not profile_b.get("ok"):
            errors.append(profile_b.get("error", "profile_b failed"))
        result["error"] = "; ".join(errors)
        return result

    if opts.full_profiles:
        result["profile_a"] = profile_a
        result["profile_b"] = profile_b

    lum_a = profile_a["luminance"]["mean"]
    lum_b = profile_b["luminance"]["mean"]
    delta_lum = _round_float(lum_b - lum_a)
    sat_a = profile_a.get("color", {}).get("saturation_mean", 0.0)
    sat_b = profile_b.get("color", {}).get("saturation_mean", 0.0)

    pixel_meta: dict = {"size_match": True, "changed_ratio": 0.0, "almost_same": True}
    try:
        img_a = load(path_a)
        img_b = load(path_b)
        if opts.max_long_edge > 0:
            img_a = resize_long_edge(img_a, opts.max_long_edge)
            img_b = resize_long_edge(img_b, opts.max_long_edge)
        if img_a.size != img_b.size:
            pixel_meta = {
                "size_match": False,
                "changed_ratio": None,
                "almost_same": False,
            }
        else:
            _, meta = diff_images(img_a, img_b)
            pixel_meta = {
                "size_match": True,
                "changed_ratio": meta["changed_ratio"],
                "almost_same": meta["changed_ratio"] <= opts.pixel_unchanged,
            }
    except ValueError:
        pixel_meta = {"size_match": False, "changed_ratio": None, "almost_same": False}

    palette_overlap = _palette_overlap(profile_a, profile_b)
    brightness_sig = abs(delta_lum) >= opts.threshold_brightness
    palette_sig = palette_overlap < (1.0 - opts.threshold_palette)
    overall = (
        pixel_meta.get("almost_same", False)
        and not brightness_sig
        and not palette_sig
    )

    opaque_a = profile_a["structure"]["opaque_ratio"]
    opaque_b = profile_b["structure"]["opaque_ratio"]
    brightness_relation = _brightness_relation(delta_lum, opts.threshold_brightness)
    if not pixel_meta["size_match"] and abs(opaque_a - opaque_b) > 0.5:
        brightness_relation = "incomparable"

    result["delta"] = {
        "luminance_mean": delta_lum,
        "luminance_mean_abs": _round_float(abs(delta_lum)),
        "saturation_mean": _round_float(sat_b - sat_a),
        "palette_overlap_ratio": palette_overlap,
    }
    result["pixel"] = pixel_meta
    result["verdict"] = {
        "brightness_relation": brightness_relation,
        "brightness_significantly_different": brightness_sig,
        "palette_significantly_different": palette_sig,
        "overall_similar": overall,
    }
    result["thresholds"] = {
        "brightness": opts.threshold_brightness,
        "palette": opts.threshold_palette,
        "pixel_unchanged": opts.pixel_unchanged,
    }

    if opts.spatial and "spatial" in profile_a and "spatial" in profile_b:
        result["spatial_a"] = profile_a["spatial"]
        result["spatial_b"] = profile_b["spatial"]
        result["spatial_delta"] = compare_spatial(profile_a["spatial"], profile_b["spatial"])

    return result


def analyze_many(paths: list[Path], *, opts: MetricsOptions | None = None) -> dict:
    items = [analyze_image(path, opts=opts) for path in paths]
    return {"version": "1.0", "kind": "profiles", "items": items}
