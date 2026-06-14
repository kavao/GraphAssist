"""Spatial / local image metrics (Phase L)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image

from graphassist.engine.content_mask import content_mask, opaque_mask


@dataclass(frozen=True)
class AnalyzeOptions:
    background: str = "transparent"
    tolerance: int = 0
    alpha_threshold: int = 128
    grid_rows: int = 3
    grid_cols: int = 3
    rois: list[dict] | None = None


def _round4(value: float) -> float:
    return round(float(value), 4)


def _luminance_mean_rgba(rgba: Image.Image, mask: Image.Image) -> float | None:
    arr = np.array(rgba, dtype=np.float32)
    m = np.array(mask, dtype=bool)
    if not m.any():
        return None
    rgb = arr[m, :3]
    y = (0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2]) / 255.0
    return _round4(float(y.mean()))


def _bbox_from_mask(mask: Image.Image) -> tuple[int, int, int, int] | None:
    bbox = mask.getbbox()
    if bbox is None:
        return None
    left, top, right, bottom = bbox
    return left, top, right - left, bottom - top


def _edge_inset(mask: Image.Image) -> dict:
    w, h = mask.size
    m = np.array(mask, dtype=bool)
    if not m.any():
        return {"top": h, "left": w, "right": w, "bottom": h}

    rows = np.any(m, axis=1)
    cols = np.any(m, axis=0)
    top = int(np.argmax(rows)) if rows.any() else h
    bottom = int(h - 1 - np.argmax(rows[::-1])) if rows.any() else h
    left = int(np.argmax(cols)) if cols.any() else w
    right = int(w - 1 - np.argmax(cols[::-1])) if cols.any() else w

    return {
        "top": top,
        "left": left,
        "right": w - 1 - right,
        "bottom": h - 1 - bottom,
    }


def _content_bbox_block(mask: Image.Image, width: int, height: int) -> dict:
    bbox = _bbox_from_mask(mask)
    if bbox is None:
        return {
            "content_bbox": None,
            "content_ratio": {"width": 0.0, "height": 0.0},
            "verdict": {
                "has_transparent_margins": False,
                "margin_left_px": 0,
                "margin_top_px": 0,
                "content_empty": True,
            },
        }
    x, y, bw, bh = bbox
    inset = _edge_inset(mask)
    return {
        "content_bbox": {"x": x, "y": y, "width": bw, "height": bh},
        "content_ratio": {
            "width": _round4(bw / width if width else 0),
            "height": _round4(bh / height if height else 0),
        },
        "verdict": {
            "has_transparent_margins": inset["left"] > 0 or inset["top"] > 0 or inset["right"] > 0 or inset["bottom"] > 0,
            "margin_left_px": inset["left"],
            "margin_top_px": inset["top"],
            "margin_right_px": inset["right"],
            "margin_bottom_px": inset["bottom"],
            "content_empty": False,
        },
    }


def _edge_verdict(inset: dict, width: int, height: int) -> dict:
    return {
        "content_touches_top": inset["top"] == 0,
        "content_touches_bottom": inset["bottom"] == 0,
        "content_touches_left": inset["left"] == 0,
        "content_touches_right": inset["right"] == 0,
        "asymmetric_horizontal": abs(inset["left"] - inset["right"]) > max(2, width // 20),
        "asymmetric_vertical": abs(inset["top"] - inset["bottom"]) > max(2, height // 20),
    }


def _grid_profile(rgba: Image.Image, mask: Image.Image, *, rows: int, cols: int) -> dict:
    w, h = rgba.size
    tiles: list[dict] = []
    lum_values: list[tuple[str, float]] = []

    for row in range(rows):
        y0 = row * h // rows
        y1 = (row + 1) * h // rows
        for col in range(cols):
            x0 = col * w // cols
            x1 = (col + 1) * w // cols
            tile_mask = mask.crop((x0, y0, x1, y1))
            tile_rgba = rgba.crop((x0, y0, x1, y1))
            m = np.array(tile_mask, dtype=bool)
            opaque_ratio = _round4(m.sum() / m.size if m.size else 0.0)
            lum = _luminance_mean_rgba(tile_rgba, tile_mask)
            tile_id = f"r{row}c{col}"
            entry: dict = {
                "id": tile_id,
                "row": row,
                "col": col,
                "opaque_ratio": opaque_ratio,
            }
            if lum is not None:
                entry["luminance_mean"] = lum
                lum_values.append((tile_id, lum))
            tiles.append(entry)

    verdict: dict = {}
    if lum_values:
        brightest = max(lum_values, key=lambda t: t[1])
        darkest = min(lum_values, key=lambda t: t[1])
        verdict["brightest_tile"] = brightest[0]
        verdict["darkest_tile"] = darkest[0]

    return {"grid": {"rows": rows, "cols": cols}, "tiles": tiles, "verdict": verdict}


def _roi_profiles(rgba: Image.Image, mask: Image.Image, rois: list[dict]) -> list[dict]:
    w, h = rgba.size
    results: list[dict] = []
    for roi in rois[:4]:
        name = roi["name"]
        x = int(roi["x"])
        y = int(roi["y"])
        rw = int(roi["width"])
        rh = int(roi["height"])
        if rw <= 0 or rh <= 0:
            continue
        x0 = max(0, min(x, w))
        y0 = max(0, min(y, h))
        x1 = max(x0, min(x0 + rw, w))
        y1 = max(y0, min(y0 + rh, h))
        tile_rgba = rgba.crop((x0, y0, x1, y1))
        tile_mask = mask.crop((x0, y0, x1, y1))
        m = np.array(tile_mask, dtype=bool)
        opaque_ratio = _round4(m.sum() / m.size if m.size else 0.0)
        lum = _luminance_mean_rgba(tile_rgba, tile_mask)
        entry: dict = {
            "name": name,
            "rect": {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0},
            "opaque_ratio": opaque_ratio,
        }
        if lum is not None:
            arr = np.array(tile_rgba, dtype=np.float32)
            rgb = arr[m, :3]
            entry["luminance"] = {
                "mean": lum,
                "std": _round4(float(((0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2]) / 255.0).std())),
            }
        results.append(entry)
    return results


def analyze_spatial(rgba: Image.Image, opts: AnalyzeOptions) -> dict:
    w, h = rgba.size
    cmask = content_mask(
        rgba,
        background=opts.background,
        tolerance=opts.tolerance,
        alpha_threshold=opts.alpha_threshold,
    )
    opaque = opaque_mask(rgba, alpha_threshold=opts.alpha_threshold)
    inset = _edge_inset(cmask)

    spatial: dict = {}
    spatial.update(_content_bbox_block(cmask, w, h))
    spatial["edge_inset"] = inset
    verdict = {**spatial.pop("verdict", {}), **_edge_verdict(inset, w, h)}
    grid = _grid_profile(rgba, opaque, rows=opts.grid_rows, cols=opts.grid_cols)
    spatial["grid"] = grid["grid"]
    spatial["tiles"] = grid["tiles"]
    verdict.update(grid["verdict"])
    spatial["verdict"] = verdict
    if opts.rois:
        spatial["rois"] = _roi_profiles(rgba, opaque, opts.rois)
    return spatial


def compare_spatial(spatial_a: dict, spatial_b: dict) -> dict:
    delta: dict = {}
    bbox_a = spatial_a.get("content_bbox")
    bbox_b = spatial_b.get("content_bbox")
    if bbox_a and bbox_b:
        delta["content_bbox"] = {
            "x": bbox_b["x"] - bbox_a["x"],
            "y": bbox_b["y"] - bbox_a["y"],
            "width": bbox_b["width"] - bbox_a["width"],
            "height": bbox_b["height"] - bbox_a["height"],
        }
    inset_a = spatial_a.get("edge_inset", {})
    inset_b = spatial_b.get("edge_inset", {})
    if inset_a and inset_b:
        delta["edge_inset"] = {k: inset_b.get(k, 0) - inset_a.get(k, 0) for k in ("top", "left", "right", "bottom")}

    roi_delta: list[dict] = []
    rois_a = {r["name"]: r for r in spatial_a.get("rois", [])}
    rois_b = {r["name"]: r for r in spatial_b.get("rois", [])}
    for name in sorted(set(rois_a) & set(rois_b)):
        la = rois_a[name].get("luminance", {}).get("mean")
        lb = rois_b[name].get("luminance", {}).get("mean")
        if la is not None and lb is not None:
            roi_delta.append({"name": name, "luminance_mean": _round4(lb - la)})
    if roi_delta:
        delta["rois"] = roi_delta

    return delta
