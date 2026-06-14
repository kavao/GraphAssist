"""画像メタデータ検査。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, UnidentifiedImageError


def inspect_image(path: Path, *, max_long_edge: int | None = None) -> dict:
    result: dict = {"path": str(path), "ok": False}
    try:
        with Image.open(path) as img:
            img.load()
            w, h = img.size
            mode = img.mode
            has_alpha = mode in {"RGBA", "LA", "PA"} or (mode == "P" and "transparency" in img.info)
            long_edge = max(w, h)
            result.update(
                {
                    "ok": True,
                    "width": w,
                    "height": h,
                    "mode": mode,
                    "format": img.format,
                    "has_alpha": has_alpha,
                    "long_edge": long_edge,
                }
            )
            if max_long_edge is not None and long_edge > max_long_edge:
                result["ok"] = False
                result["error"] = f"long_edge {long_edge} exceeds max {max_long_edge}"
    except (UnidentifiedImageError, OSError) as exc:
        result["error"] = str(exc)
    return result


def inspect_many(paths: list[Path], *, max_long_edge: int | None = None) -> list[dict]:
    return [inspect_image(path, max_long_edge=max_long_edge) for path in paths]
