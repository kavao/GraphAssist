"""executor 更新。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from graphassist.engine.canvas import load, save
from graphassist.engine.ops_adjust import apply_adjust
from graphassist.engine.ops_color import apply_grayscale, apply_sepia
from graphassist.engine.ops_composite import apply_composite
from graphassist.engine.ops_filter import apply_blur, apply_sharpen
from graphassist.engine.ops_geometry import (
    apply_border,
    apply_crop,
    apply_extend,
    apply_resize,
    apply_rotate,
)
from graphassist.engine.ops_mosaic import apply_to_mosaic
from graphassist.engine.ops_text import apply_text
from graphassist.engine.ops_tone import apply_curve, apply_posterize, apply_quantize
from graphassist.engine.ops_trim import apply_flatten, apply_trim
from graphassist.schema.job import ImageJob
from graphassist.schema.paths import normalize_manifest_path, resolve_batch_chained_input
from graphassist.schema.ops import (
    AdjustOp,
    BlurOp,
    BorderOp,
    CompositeOp,
    CropOp,
    CurveOp,
    ExtendOp,
    FlattenOp,
    GrayscaleOp,
    Operation,
    PosterizeOp,
    QuantizeOp,
    ResizeOp,
    RotateOp,
    SepiaOp,
    SharpenOp,
    TextOp,
    ToMosaicOp,
    TrimOp,
)


def apply_operation(img: Image.Image, op: Operation, *, root: Path) -> Image.Image:
    if isinstance(op, ResizeOp):
        return apply_resize(img, op)
    if isinstance(op, CropOp):
        return apply_crop(img, op)
    if isinstance(op, ExtendOp):
        return apply_extend(img, op)
    if isinstance(op, RotateOp):
        return apply_rotate(img, op)
    if isinstance(op, BorderOp):
        return apply_border(img, op)
    if isinstance(op, CompositeOp):
        return apply_composite(img, op, root=root)
    if isinstance(op, TextOp):
        return apply_text(img, op, root=root)
    if isinstance(op, TrimOp):
        return apply_trim(img, op)
    if isinstance(op, FlattenOp):
        return apply_flatten(img, op)
    if isinstance(op, AdjustOp):
        return apply_adjust(img, op)
    if isinstance(op, GrayscaleOp):
        return apply_grayscale(img, op)
    if isinstance(op, SepiaOp):
        return apply_sepia(img, op)
    if isinstance(op, CurveOp):
        return apply_curve(img, op)
    if isinstance(op, QuantizeOp):
        return apply_quantize(img, op)
    if isinstance(op, PosterizeOp):
        return apply_posterize(img, op)
    if isinstance(op, BlurOp):
        return apply_blur(img, op)
    if isinstance(op, SharpenOp):
        return apply_sharpen(img, op)
    if isinstance(op, ToMosaicOp):
        return apply_to_mosaic(img, op, root=root)
    raise ValueError(f"unsupported operation: {op}")


def execute_job(
    job: ImageJob,
    *,
    root: Path,
    dry_run: bool = False,
    chained_input: bool = False,
) -> tuple[Path, list[str]]:
    if chained_input:
        assert job.input is not None
        input_path = resolve_batch_chained_input(job.input, root=root, must_exist=not dry_run)
    else:
        input_path = job.resolved_input(root=root, must_exist=not dry_run)
    output_path = job.resolved_output()
    steps: list[str] = [f"load {job.display_input}"]

    for op in job.operations:
        steps.append(f"{op.type} {op.model_dump(exclude={'type'})}")

    steps.append(f"save {job.output}")

    if dry_run:
        return output_path, steps

    img = load(input_path)
    for op in job.operations:
        img = apply_operation(img, op, root=root)
    save(img, output_path)
    return output_path, steps
