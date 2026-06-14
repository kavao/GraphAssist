"""executor 更新。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from graphassist.engine.canvas import load, save
from graphassist.engine.ops_composite import apply_composite
from graphassist.engine.ops_geometry import (
    apply_border,
    apply_crop,
    apply_extend,
    apply_resize,
    apply_rotate,
)
from graphassist.engine.ops_text import apply_text
from graphassist.engine.ops_trim import apply_flatten, apply_trim
from graphassist.schema.job import ImageJob
from graphassist.schema.ops import (
    BorderOp,
    CompositeOp,
    CropOp,
    ExtendOp,
    FlattenOp,
    Operation,
    ResizeOp,
    RotateOp,
    TextOp,
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
    raise ValueError(f"unsupported operation: {op}")


def execute_job(job: ImageJob, *, root: Path, dry_run: bool = False) -> tuple[Path, list[str]]:
    input_path = job.resolved_input(must_exist=not dry_run)
    output_path = job.resolved_output()
    steps: list[str] = [f"load {job.input}"]

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
