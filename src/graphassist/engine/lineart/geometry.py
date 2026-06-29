"""Normalize LineArt shapes into geometry primitives for validation."""

from __future__ import annotations

import math
from dataclasses import dataclass

from graphassist.engine.lineart.smooth import catmull_rom_to_commands
from graphassist.schema.lineart import (
    EllipseShape,
    GroupShape,
    LineArtDocument,
    LineArtShape,
    PathCommand,
    PathShape,
    PolygonShape,
    RectShape,
    SmoothPathShape,
    StarShape,
    Transform,
)

Point = tuple[float, float]
BBox = tuple[float, float, float, float]
Matrix = tuple[float, float, float, float, float, float]


@dataclass(frozen=True)
class ShapeGeometry:
    id: str
    type: str
    layer_id: str
    role: str | None
    container_id: str | None
    allow_overlap: bool | None
    points: tuple[Point, ...]
    bbox: BBox
    closed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "type": self.type,
            "layer_id": self.layer_id,
            "role": self.role,
            "container_id": self.container_id,
            "allow_overlap": self.allow_overlap,
            "points": [[x, y] for x, y in self.points],
            "bbox": {
                "x": self.bbox[0],
                "y": self.bbox[1],
                "width": self.bbox[2],
                "height": self.bbox[3],
            },
            "closed": self.closed,
        }


def normalize_lineart_geometry(document: LineArtDocument) -> list[ShapeGeometry]:
    geometries: list[ShapeGeometry] = []
    identity = _identity()
    for layer in document.layers:
        if not layer.visible:
            continue
        for shape in layer.shapes:
            _collect_shape_geometry(shape, layer_id=layer.id, matrix=identity, geometries=geometries)
    return geometries


def _collect_shape_geometry(
    shape: LineArtShape,
    *,
    layer_id: str,
    matrix: Matrix,
    geometries: list[ShapeGeometry],
) -> None:
    if not shape.visible:
        return
    shape_matrix = _multiply(matrix, _transform_matrix(shape.transform))
    if isinstance(shape, GroupShape):
        for child in shape.shapes:
            _collect_shape_geometry(child, layer_id=layer_id, matrix=shape_matrix, geometries=geometries)
        return

    points, closed = _shape_points(shape)
    transformed = tuple(_apply(shape_matrix, point) for point in points)
    geometries.append(
        ShapeGeometry(
            id=shape.id,
            type=shape.type,
            layer_id=layer_id,
            role=shape.role,
            container_id=shape.container_id,
            allow_overlap=shape.allow_overlap,
            points=transformed,
            bbox=_bbox(transformed),
            closed=closed,
        )
    )


def _shape_points(shape: LineArtShape) -> tuple[tuple[Point, ...], bool]:
    if isinstance(shape, RectShape):
        points = (
            (shape.x, shape.y),
            (shape.x + shape.width, shape.y),
            (shape.x + shape.width, shape.y + shape.height),
            (shape.x, shape.y + shape.height),
        )
        return points, True
    if isinstance(shape, EllipseShape):
        return _ellipse_points(shape), True
    if isinstance(shape, PolygonShape):
        return tuple((point[0], point[1]) for point in shape.points), True
    if isinstance(shape, StarShape):
        return _star_points(shape), True
    if isinstance(shape, SmoothPathShape):
        commands = catmull_rom_to_commands(shape.points, closed=shape.closed)
        return _commands_to_points(commands, closed=shape.closed), shape.closed
    if isinstance(shape, PathShape):
        return _commands_to_points(shape.commands, closed=shape.closed), shape.closed
    raise TypeError(f"unsupported shape for geometry: {type(shape)!r}")


def _commands_to_points(commands: list[PathCommand], *, closed: bool) -> tuple[Point, ...]:
    points: list[Point] = []
    current: Point | None = None
    start: Point | None = None
    for command in commands:
        if command.command == "M":
            current = (command.values[0], command.values[1])
            start = current
            points.append(current)
        elif command.command == "L":
            current = (command.values[0], command.values[1])
            points.append(current)
        elif command.command == "Q":
            if current is None:
                continue
            control = (command.values[0], command.values[1])
            end = (command.values[2], command.values[3])
            points.extend(_sample_quadratic(current, control, end)[1:])
            current = end
        elif command.command == "C":
            if current is None:
                continue
            control_a = (command.values[0], command.values[1])
            control_b = (command.values[2], command.values[3])
            end = (command.values[4], command.values[5])
            points.extend(_sample_cubic(current, control_a, control_b, end)[1:])
            current = end
        elif command.command == "Z" and start is not None:
            current = start
            points.append(start)
    if closed and start is not None and points[-1] != start:
        points.append(start)
    return tuple(points)


def _sample_quadratic(start: Point, control: Point, end: Point, *, steps: int = 12) -> list[Point]:
    result: list[Point] = []
    for index in range(steps + 1):
        t = index / steps
        mt = 1 - t
        result.append(
            (
                mt * mt * start[0] + 2 * mt * t * control[0] + t * t * end[0],
                mt * mt * start[1] + 2 * mt * t * control[1] + t * t * end[1],
            )
        )
    return result


def _sample_cubic(start: Point, control_a: Point, control_b: Point, end: Point, *, steps: int = 16) -> list[Point]:
    result: list[Point] = []
    for index in range(steps + 1):
        t = index / steps
        mt = 1 - t
        result.append(
            (
                mt**3 * start[0] + 3 * mt * mt * t * control_a[0] + 3 * mt * t * t * control_b[0] + t**3 * end[0],
                mt**3 * start[1] + 3 * mt * mt * t * control_a[1] + 3 * mt * t * t * control_b[1] + t**3 * end[1],
            )
        )
    return result


def _ellipse_points(shape: EllipseShape, *, steps: int = 32) -> tuple[Point, ...]:
    return tuple(
        (
            shape.cx + math.cos(index * math.tau / steps) * shape.rx,
            shape.cy + math.sin(index * math.tau / steps) * shape.ry,
        )
        for index in range(steps)
    )


def _star_points(shape: StarShape) -> tuple[Point, ...]:
    inner_radius = shape.inner_radius if shape.inner_radius is not None else shape.outer_radius * 0.5
    angle_offset = math.radians(shape.rotation) - math.pi / 2
    points: list[Point] = []
    for index in range(shape.points * 2):
        radius = shape.outer_radius if index % 2 == 0 else inner_radius
        angle = angle_offset + index * math.pi / shape.points
        points.append((shape.cx + math.cos(angle) * radius, shape.cy + math.sin(angle) * radius))
    return tuple(points)


def _bbox(points: tuple[Point, ...]) -> BBox:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x = min(xs)
    min_y = min(ys)
    return (min_x, min_y, max(xs) - min_x, max(ys) - min_y)


def _identity() -> Matrix:
    return (1, 0, 0, 1, 0, 0)


def _transform_matrix(transform: Transform | None) -> Matrix:
    matrix = _identity()
    if transform is None:
        return matrix
    if transform.translate is not None:
        matrix = _multiply(matrix, (1, 0, 0, 1, transform.translate[0], transform.translate[1]))
    if transform.rotate is not None:
        angle = math.radians(transform.rotate)
        rotate = (math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), 0, 0)
        if transform.rotate_origin is not None:
            ox, oy = transform.rotate_origin
            rotate = _multiply(_multiply((1, 0, 0, 1, ox, oy), rotate), (1, 0, 0, 1, -ox, -oy))
        matrix = _multiply(matrix, rotate)
    if transform.scale is not None:
        if isinstance(transform.scale, float):
            sx = sy = transform.scale
        else:
            sx, sy = transform.scale
        matrix = _multiply(matrix, (sx, 0, 0, sy, 0, 0))
    return matrix


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    la, lb, lc, ld, le, lf = left
    ra, rb, rc, rd, re, rf = right
    return (
        la * ra + lc * rb,
        lb * ra + ld * rb,
        la * rc + lc * rd,
        lb * rc + ld * rd,
        la * re + lc * rf + le,
        lb * re + ld * rf + lf,
    )


def _apply(matrix: Matrix, point: Point) -> Point:
    a, b, c, d, e, f = matrix
    x, y = point
    return (a * x + c * y + e, b * x + d * y + f)
