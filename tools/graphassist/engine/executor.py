"""ImageJob operation を順次適用。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from tools.graphassist.engine.canvas import load, save
from tools.graphassist.engine.ops_composite import apply_composite
from tools.graphassist.engine.ops_geometry import (
    apply_border,
    apply_crop,
    apply_extend,
    apply_resize,
    apply_rotate,
)
from tools.graphassist.schema.job import ImageJob
from tools.graphassist.schema.ops import (
    BorderOp,
    CompositeOp,
    CropOp,
    ExtendOp,
    Operation,
    ResizeOp,
    RotateOp,
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
