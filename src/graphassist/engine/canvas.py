"""RGBA キャンバスの load / save と基本変換。"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif"}

FillColor = Literal["transparent", "white", "black"]


def is_image_path(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def load(path: Path) -> Image.Image:
    with Image.open(path) as img:
        return img.convert("RGBA")


def save(
    img: Image.Image,
    path: Path,
    *,
    fmt: str | None = None,
    quality: int = 85,
    dpi: tuple[float, float] | None = None,
    strip_exif: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out_fmt = (fmt or path.suffix.lstrip(".")).upper()
    if out_fmt == "JPG":
        out_fmt = "JPEG"

    working = img
    if out_fmt == "JPEG":
        working = _flatten_background(working, "white")
    elif out_fmt == "WEBP" and working.mode != "RGBA":
        working = working.convert("RGBA")

    save_kwargs: dict = {}
    if out_fmt in {"JPEG", "WEBP"}:
        save_kwargs["quality"] = quality
    if dpi is not None:
        save_kwargs["dpi"] = dpi
    if strip_exif and out_fmt == "JPEG":
        save_kwargs["exif"] = b""

    working.save(path, format=out_fmt, **save_kwargs)


def _flatten_background(img: Image.Image, fill: FillColor) -> Image.Image:
    if fill == "transparent":
        return img.convert("RGBA")
    rgb = {"white": (255, 255, 255), "black": (0, 0, 0)}[fill]
    base = Image.new("RGBA", img.size, rgb + (255,))
    base.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
    return base.convert("RGB")


def _fill_rgba(fill: FillColor) -> tuple[int, int, int, int]:
    if fill == "transparent":
        return (0, 0, 0, 0)
    if fill == "white":
        return (255, 255, 255, 255)
    return (0, 0, 0, 255)


def resize_long_edge(img: Image.Image, long_edge: int) -> Image.Image:
    w, h = img.size
    if max(w, h) <= long_edge:
        return img.copy()
    if w >= h:
        new_w = long_edge
        new_h = max(1, round(h * long_edge / w))
    else:
        new_h = long_edge
        new_w = max(1, round(w * long_edge / h))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def resize_wh(img: Image.Image, width: int | None, height: int | None) -> Image.Image:
    w, h = img.size
    target_w = width if width is not None else w
    target_h = height if height is not None else h
    if (target_w, target_h) == (w, h):
        return img.copy()
    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)


def pad_square(img: Image.Image, fill: FillColor = "transparent") -> Image.Image:
    w, h = img.size
    side = max(w, h)
    if w == h == side:
        return img.copy()
    canvas = Image.new("RGBA", (side, side), _fill_rgba(fill))
    canvas.paste(img, ((side - w) // 2, (side - h) // 2), img if img.mode == "RGBA" else None)
    return canvas


def _format_ext(fmt: str) -> str:
    f = fmt.lower()
    return ".jpg" if f in {"jpeg", "jpg"} else f".{f}"


def output_path_for(
    input_path: Path,
    output: Path,
    *,
    input_is_dir: bool,
    fmt: str,
    index: int | None = None,
    numbered: bool = False,
) -> Path:
    ext = _format_ext(fmt)

    if input_is_dir:
        stem = f"{index:04d}" if numbered and index is not None else input_path.stem
        return output / f"{stem}{ext}"

    if output.suffix:
        return output.with_suffix(ext)
    return Path(str(output) + ext)
