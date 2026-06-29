"""LineArt validation foundation."""

from __future__ import annotations

import math
from pathlib import Path

from graphassist.engine.lineart.geometry import BBox, Point, ShapeGeometry, normalize_lineart_geometry
from graphassist.schema.lineart import GroupShape, LineArtDocument, LineArtShape, Severity
from graphassist.schema.lineart_validation import (
    RepairHint,
    ValidationIssue,
    ValidationReport,
    ValidationSource,
    ValidationSummary,
)


def validate_lineart_document(document: LineArtDocument, *, input_path: str) -> ValidationReport:
    geometries = normalize_lineart_geometry(document)
    by_id = {geometry.id: geometry for geometry in geometries}
    shape_ids = {geometry.id for geometry in geometries}
    issues: list[ValidationIssue] = []
    for shape in _iter_shapes(document):
        _validate_metadata_references(shape, shape_ids=shape_ids, issues=issues)
        _validate_containment(shape, by_id=by_id, issues=issues)
        _validate_connector_alignment(shape, by_id=by_id, issues=issues)
        _validate_line_intersections(shape, by_id=by_id, issues=issues)
    _validate_overlaps(geometries, issues=issues)

    summary = ValidationSummary(
        errors=sum(1 for issue in issues if issue.severity == "error"),
        warnings=sum(1 for issue in issues if issue.severity == "warning"),
        info=sum(1 for issue in issues if issue.severity == "info"),
        geometries=len(geometries),
    )
    if summary.errors:
        result = "failed"
    elif summary.warnings:
        result = "warning_only"
    else:
        result = "passed"
    return ValidationReport(
        validation_result=result,
        source=ValidationSource(document_id=Path(input_path).stem, input_path=input_path),
        summary=summary,
        issues=issues,
    )


def lineart_geometry_snapshot(document: LineArtDocument) -> list[dict[str, object]]:
    return [geometry.to_dict() for geometry in normalize_lineart_geometry(document)]


def _iter_shapes(document: LineArtDocument):
    for layer in document.layers:
        if not layer.visible:
            continue
        for shape in layer.shapes:
            yield from _iter_shape_tree(shape)


def _iter_shape_tree(shape: LineArtShape):
    if not shape.visible:
        return
    yield shape
    if isinstance(shape, GroupShape):
        for child in shape.shapes:
            yield from _iter_shape_tree(child)


def _validate_metadata_references(
    shape: LineArtShape,
    *,
    shape_ids: set[str],
    issues: list[ValidationIssue],
) -> None:
    if shape.container_id is not None and shape.container_id not in shape_ids:
        issues.append(_unknown_reference(len(issues) + 1, shape.id, "container_id", shape.container_id, severity="error"))
    if shape.connects_to is not None:
        if shape.connects_to.from_ not in shape_ids:
            issues.append(
                _unknown_reference(len(issues) + 1, shape.id, "connects_to.from", shape.connects_to.from_, severity="error")
            )
        if shape.connects_to.to not in shape_ids:
            issues.append(_unknown_reference(len(issues) + 1, shape.id, "connects_to.to", shape.connects_to.to, severity="error"))
    if shape.validation is None:
        return
    expected = shape.validation.expected
    if isinstance(expected, dict):
        return
    severity = shape.validation.severity
    if expected.inside is not None and expected.inside not in shape_ids:
        issues.append(_unknown_reference(len(issues) + 1, shape.id, "validation.expected.inside", expected.inside, severity=severity))
    if expected.near is not None and expected.near.target not in shape_ids:
        issues.append(
            _unknown_reference(
                len(issues) + 1,
                shape.id,
                "validation.expected.near.target",
                expected.near.target,
                severity=severity,
            )
        )
    if expected.touches is not None:
        for target in expected.touches:
            if target not in shape_ids:
                issues.append(_unknown_reference(len(issues) + 1, shape.id, "validation.expected.touches", target, severity=severity))


def _validate_containment(
    shape: LineArtShape,
    *,
    by_id: dict[str, ShapeGeometry],
    issues: list[ValidationIssue],
) -> None:
    geometry = by_id.get(shape.id)
    if geometry is None:
        return
    expected_container = shape.container_id
    severity: Severity = "warning"
    if shape.validation is not None and not isinstance(shape.validation.expected, dict):
        severity = shape.validation.severity
        expected_container = shape.validation.expected.inside or expected_container
    if expected_container is None or expected_container not in by_id:
        return
    container = by_id[expected_container]
    if _bbox_contains(container.bbox, geometry.bbox):
        return
    issues.append(
        ValidationIssue(
            issue_id=_next_issue_id(issues),
            type="outside_container",
            severity=severity,
            object_ids=[shape.id, expected_container],
            position=_bbox_center(geometry.bbox),
            metric={"target_bbox": _bbox_dict(geometry.bbox), "container_bbox": _bbox_dict(container.bbox)},
            message=f"{shape.id} is outside {expected_container}.",
            repair_hint=RepairHint(action="move", target=shape.id, toward=expected_container, constraints={"inside": expected_container}),
        )
    )


def _validate_connector_alignment(
    shape: LineArtShape,
    *,
    by_id: dict[str, ShapeGeometry],
    issues: list[ValidationIssue],
) -> None:
    if shape.connects_to is None:
        return
    connector = by_id.get(shape.id)
    source = by_id.get(shape.connects_to.from_)
    target = by_id.get(shape.connects_to.to)
    if connector is None or source is None or target is None or len(connector.points) < 2:
        return
    start = connector.points[0]
    end = connector.points[-1]
    max_distance = _max_distance(shape, default=4.0)
    start_distance = _point_to_bbox_distance(start, source.bbox)
    end_distance = _point_to_bbox_distance(end, target.bbox)
    if start_distance <= max_distance and end_distance <= max_distance:
        return
    issues.append(
        ValidationIssue(
            issue_id=_next_issue_id(issues),
            type="connector_misaligned",
            severity=_validation_severity(shape, default="error"),
            object_ids=[shape.id, shape.connects_to.from_, shape.connects_to.to],
            position=list(end if end_distance > start_distance else start),
            metric={
                "from_distance": round(start_distance, 4),
                "to_distance": round(end_distance, 4),
                "max_allowed_distance": max_distance,
            },
            message=f"{shape.id} does not connect {shape.connects_to.from_} to {shape.connects_to.to}.",
            repair_hint=RepairHint(
                action="move_endpoint",
                target=shape.id,
                anchor="to" if end_distance > start_distance else "from",
                toward=shape.connects_to.to if end_distance > start_distance else shape.connects_to.from_,
            ),
        )
    )


def _validate_line_intersections(
    shape: LineArtShape,
    *,
    by_id: dict[str, ShapeGeometry],
    issues: list[ValidationIssue],
) -> None:
    if shape.validation is None or isinstance(shape.validation.expected, dict):
        return
    if shape.validation.expected.no_intersections is not True:
        return
    geometry = by_id.get(shape.id)
    if geometry is None:
        return
    for other in by_id.values():
        if other.id == geometry.id:
            continue
        if not _bbox_intersects(geometry.bbox, other.bbox):
            continue
        point = _first_segment_intersection(geometry.points, other.points)
        if point is None:
            continue
        issues.append(
            ValidationIssue(
                issue_id=_next_issue_id(issues),
                type="line_intersection",
                severity=shape.validation.severity,
                object_ids=[geometry.id, other.id],
                position=[round(point[0], 4), round(point[1], 4)],
                metric={"mode": "polyline_segment"},
                message=f"{geometry.id} intersects {other.id}.",
                repair_hint=RepairHint(action="reroute", target=geometry.id, constraints={"avoid": other.id}),
            )
        )
        return


def _validate_overlaps(geometries: list[ShapeGeometry], *, issues: list[ValidationIssue]) -> None:
    watched = [geometry for geometry in geometries if geometry.allow_overlap is False and geometry.closed]
    for index, geometry in enumerate(watched):
        for other in geometries:
            if other.id == geometry.id or not other.closed:
                continue
            if _is_container_pair(geometry, other):
                continue
            area = _bbox_overlap_area(geometry.bbox, other.bbox)
            if area <= 0:
                continue
            issues.append(
                ValidationIssue(
                    issue_id=_next_issue_id(issues),
                    type="overlap",
                    severity="warning",
                    object_ids=[geometry.id, other.id],
                    position=_bbox_center(_bbox_intersection(geometry.bbox, other.bbox)),
                    metric={"overlap_area": round(area, 4), "mode": "bbox"},
                    message=f"{geometry.id} overlaps {other.id}.",
                    repair_hint=RepairHint(action="keep_clear", target=geometry.id, constraints={"avoid": other.id}),
                )
            )
            break
        if index > len(watched):  # pragma: no cover - defensive no-op
            break


def _unknown_reference(index: int, shape_id: str, field: str, target: str, *, severity: str) -> ValidationIssue:
    return ValidationIssue(
        issue_id=f"LV-{index:04d}",
        type="metadata_reference_missing",
        severity=severity,
        object_ids=[shape_id, target],
        metric={"field": field},
        message=f"{shape_id} references missing shape {target} in {field}.",
    )


def _next_issue_id(issues: list[ValidationIssue]) -> str:
    return f"LV-{len(issues) + 1:04d}"


def _validation_severity(shape: LineArtShape, *, default: Severity) -> Severity:
    if shape.validation is None:
        return default
    return shape.validation.severity


def _max_distance(shape: LineArtShape, *, default: float) -> float:
    if shape.validation is None or isinstance(shape.validation.expected, dict):
        return default
    if shape.validation.expected.near is None:
        return default
    return shape.validation.expected.near.max_distance


def _bbox_contains(container: BBox, target: BBox) -> bool:
    cx, cy, cw, ch = container
    tx, ty, tw, th = target
    return tx >= cx and ty >= cy and tx + tw <= cx + cw and ty + th <= cy + ch


def _bbox_intersects(a: BBox, b: BBox) -> bool:
    return _bbox_overlap_area(a, b) > 0


def _bbox_overlap_area(a: BBox, b: BBox) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    overlap_w = min(ax + aw, bx + bw) - max(ax, bx)
    overlap_h = min(ay + ah, by + bh) - max(ay, by)
    if overlap_w <= 0 or overlap_h <= 0:
        return 0.0
    return overlap_w * overlap_h


def _bbox_intersection(a: BBox, b: BBox) -> BBox:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x = max(ax, bx)
    y = max(ay, by)
    return (x, y, min(ax + aw, bx + bw) - x, min(ay + ah, by + bh) - y)


def _bbox_center(bbox: BBox) -> list[float]:
    x, y, w, h = bbox
    return [round(x + w / 2, 4), round(y + h / 2, 4)]


def _bbox_dict(bbox: BBox) -> dict[str, float]:
    return {"x": bbox[0], "y": bbox[1], "width": bbox[2], "height": bbox[3]}


def _is_container_pair(a: ShapeGeometry, b: ShapeGeometry) -> bool:
    return a.container_id == b.id or b.container_id == a.id or a.role == "container" or b.role == "container"


def _point_to_bbox_distance(point: Point, bbox: BBox) -> float:
    x, y = point
    bx, by, bw, bh = bbox
    dx = max(bx - x, 0.0, x - (bx + bw))
    dy = max(by - y, 0.0, y - (by + bh))
    return math.hypot(dx, dy)


def _first_segment_intersection(points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> Point | None:
    for a1, a2 in zip(points_a, points_a[1:]):
        for b1, b2 in zip(points_b, points_b[1:]):
            point = _segment_intersection(a1, a2, b1, b2)
            if point is not None:
                return point
    return None


def _segment_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> Point | None:
    ax, ay = a1
    bx, by = a2
    cx, cy = b1
    dx, dy = b2
    denominator = (ax - bx) * (cy - dy) - (ay - by) * (cx - dx)
    if abs(denominator) < 1e-9:
        return None
    px = ((ax * by - ay * bx) * (cx - dx) - (ax - bx) * (cx * dy - cy * dx)) / denominator
    py = ((ax * by - ay * bx) * (cy - dy) - (ay - by) * (cx * dy - cy * dx)) / denominator
    if _within_segment(px, py, a1, a2) and _within_segment(px, py, b1, b2):
        if _is_shared_endpoint((px, py), a1, a2, b1, b2):
            return None
        return (px, py)
    return None


def _within_segment(x: float, y: float, start: Point, end: Point) -> bool:
    epsilon = 1e-7
    return (
        min(start[0], end[0]) - epsilon <= x <= max(start[0], end[0]) + epsilon
        and min(start[1], end[1]) - epsilon <= y <= max(start[1], end[1]) + epsilon
    )


def _is_shared_endpoint(point: Point, a1: Point, a2: Point, b1: Point, b2: Point) -> bool:
    endpoints = (a1, a2, b1, b2)
    return sum(_points_close(point, endpoint) for endpoint in endpoints) >= 2


def _points_close(a: Point, b: Point) -> bool:
    return abs(a[0] - b[0]) < 1e-7 and abs(a[1] - b[1]) < 1e-7
