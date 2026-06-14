"""一括 convert の処理本体。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from graphassist.engine.canvas import (
    IMAGE_EXTENSIONS,
    is_image_path,
    load,
    output_path_for,
    pad_square,
    resize_long_edge,
    resize_wh,
    save,
)


@dataclass
class ConvertOptions:
    fmt: str = "png"
    long_edge: int | None = None
    width: int | None = None
    height: int | None = None
    square: bool = False
    square_fill: str = "transparent"
    quality: int = 85
    dpi: float | None = None
    strip_exif: bool = False
    numbered: bool = False


def collect_inputs(path: Path) -> list[Path]:
    if path.is_file():
        if not is_image_path(path):
            raise ValueError(f"not an image file: {path}")
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(path)
    files = sorted(p for p in path.iterdir() if p.is_file() and is_image_path(p))
    if not files:
        raise ValueError(f"no images in directory: {path}")
    return files


def apply_transforms(img, opts: ConvertOptions):
    out = img
    if opts.long_edge is not None:
        out = resize_long_edge(out, opts.long_edge)
    if opts.width is not None or opts.height is not None:
        out = resize_wh(out, opts.width, opts.height)
    if opts.square:
        fill = opts.square_fill
        if fill not in {"transparent", "white", "black"}:
            raise ValueError(f"unsupported square fill: {fill}")
        out = pad_square(out, fill)  # type: ignore[arg-type]
    return out


def run_convert(input_path: Path, output_path: Path, opts: ConvertOptions) -> list[Path]:
    inputs = collect_inputs(input_path)
    input_is_dir = input_path.is_dir()

    if input_is_dir:
        output_path.mkdir(parents=True, exist_ok=True)
    elif output_path.suffix == "":
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for i, src in enumerate(inputs, start=1):
        img = load(src)
        img = apply_transforms(img, opts)
        if input_is_dir or not output_path.suffix:
            dst = output_path_for(
                src,
                output_path,
                input_is_dir=input_is_dir,
                fmt=opts.fmt,
                index=i,
                numbered=opts.numbered,
            )
        else:
            dst = output_path_for(
                src,
                output_path,
                input_is_dir=False,
                fmt=opts.fmt,
                index=i,
                numbered=False,
            )
        dpi_tuple = (opts.dpi, opts.dpi) if opts.dpi is not None else None
        save(
            img,
            dst,
            fmt=opts.fmt,
            quality=opts.quality,
            dpi=dpi_tuple,
            strip_exif=opts.strip_exif,
        )
        created.append(dst)
    return created
