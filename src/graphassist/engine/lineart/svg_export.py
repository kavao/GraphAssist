"""LineArt SVG export."""

from __future__ import annotations

import math
from html import escape
from pathlib import Path

from graphassist.engine.lineart.smooth import catmull_rom_to_commands
from graphassist.schema.lineart import (
    ClipPathDefinition,
    EllipseShape,
    GradientFill,
    GradientStop,
    GroupShape,
    LineArtDocument,
    LinearGradient,
    LineArtShape,
    PathCommand,
    PathShape,
    PolygonShape,
    RadialGradient,
    RectShape,
    SmoothPathShape,
    StarShape,
    Stroke,
    Transform,
)


def export_svg(document: LineArtDocument) -> str:
    attrs = [
        'xmlns="http://www.w3.org/2000/svg"',
        f'width="{document.canvas.width}"',
        f'height="{document.canvas.height}"',
        f'viewBox="0 0 {document.canvas.width} {document.canvas.height}"',
    ]
    lines = [f"<svg {' '.join(attrs)}>"]
    definition_lines = _definitions_to_svg(document)
    if definition_lines:
        lines.append("  <defs>")
        lines.extend(f"    {line}" for line in definition_lines)
        lines.append("  </defs>")
    if document.canvas.background != "transparent":
        lines.append(
            f'  <rect width="100%" height="100%" fill="{escape(document.canvas.background)}" />'
        )
    for layer in document.layers:
        if not layer.visible:
            continue
        lines.append(f'  <g id="{escape(layer.id)}">')
        for shape in layer.shapes:
            if not shape.visible:
                continue
            lines.extend(_shape_to_svg(shape, indent=4))
        lines.append("  </g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def write_svg(document: LineArtDocument, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(export_svg(document), encoding="utf-8")
    return output


def _definitions_to_svg(document: LineArtDocument) -> list[str]:
    lines: list[str] = []
    for gradient_id, gradient in document.definitions.gradients.items():
        if isinstance(gradient, LinearGradient):
            lines.extend(_linear_gradient_to_svg(gradient_id, gradient))
        elif isinstance(gradient, RadialGradient):
            lines.extend(_radial_gradient_to_svg(gradient_id, gradient))
    for clip_path_id, clip_path in document.definitions.clip_paths.items():
        lines.extend(_clip_path_to_svg(clip_path_id, clip_path))
    return lines


def _linear_gradient_to_svg(gradient_id: str, gradient: LinearGradient) -> list[str]:
    attrs = [
        f'id="{escape(gradient_id)}"',
        f'gradientUnits="{gradient.units}"',
        f'x1="{_fmt(gradient.from_[0])}"',
        f'y1="{_fmt(gradient.from_[1])}"',
        f'x2="{_fmt(gradient.to[0])}"',
        f'y2="{_fmt(gradient.to[1])}"',
    ]
    return [
        f"<linearGradient {' '.join(attrs)}>",
        *[f"  {_stop_to_svg(stop)}" for stop in gradient.stops],
        "</linearGradient>",
    ]


def _radial_gradient_to_svg(gradient_id: str, gradient: RadialGradient) -> list[str]:
    attrs = [
        f'id="{escape(gradient_id)}"',
        f'gradientUnits="{gradient.units}"',
        f'cx="{_fmt(gradient.center[0])}"',
        f'cy="{_fmt(gradient.center[1])}"',
        f'r="{_fmt(gradient.radius)}"',
        f'fx="{_fmt(gradient.focal[0])}"' if gradient.focal is not None else "",
        f'fy="{_fmt(gradient.focal[1])}"' if gradient.focal is not None else "",
    ]
    return [
        f"<radialGradient {' '.join(attr for attr in attrs if attr)}>",
        *[f"  {_stop_to_svg(stop)}" for stop in gradient.stops],
        "</radialGradient>",
    ]


def _stop_to_svg(stop: GradientStop) -> str:
    attrs = [
        f'offset="{_fmt(stop.offset * 100)}%"',
        f'stop-color="{escape(stop.color)}"',
        f'stop-opacity="{_fmt(stop.opacity)}"' if stop.opacity is not None else "",
    ]
    return f"<stop {' '.join(attr for attr in attrs if attr)} />"


def _clip_path_to_svg(clip_path_id: str, clip_path: ClipPathDefinition) -> list[str]:
    lines = [f'<clipPath id="{escape(clip_path_id)}">']
    for shape in clip_path.shapes:
        lines.extend(_shape_to_svg(shape, indent=2, include_style=False))
    lines.append("</clipPath>")
    return lines


def _shape_to_svg(shape: LineArtShape, *, indent: int = 0, include_style: bool = True) -> list[str]:
    prefix = " " * indent
    if isinstance(shape, GroupShape):
        attrs = [
            f'id="{escape(shape.id)}"',
            *_common_attrs(shape, include_clip=include_style),
        ]
        lines = [f"{prefix}<g {' '.join(attr for attr in attrs if attr)}>"]
        for child in shape.shapes:
            if child.visible:
                lines.extend(_shape_to_svg(child, indent=indent + 2, include_style=include_style))
        lines.append(f"{prefix}</g>")
        return lines
    if isinstance(shape, RectShape):
        return [prefix + _rect_to_svg(shape, include_style=include_style)]
    if isinstance(shape, EllipseShape):
        return [prefix + _ellipse_to_svg(shape, include_style=include_style)]
    if isinstance(shape, PolygonShape):
        return [prefix + _polygon_to_svg(shape, include_style=include_style)]
    if isinstance(shape, StarShape):
        return [prefix + _polygon_to_svg(shape, points=_star_points(shape), include_style=include_style)]

    if isinstance(shape, SmoothPathShape):
        commands = catmull_rom_to_commands(shape.points, closed=shape.closed)
        closed = shape.closed
    elif isinstance(shape, PathShape):
        commands = shape.commands
        closed = shape.closed
    else:  # pragma: no cover - discriminated union guard
        raise TypeError(f"unsupported shape: {type(shape)!r}")

    d = _commands_to_d(commands, closed=closed)
    attrs = [
        f'id="{escape(shape.id)}"',
        f'd="{escape(d)}"',
        *(_style_attrs(shape) if include_style else _clip_style_attrs()),
        *_common_attrs(shape, include_clip=include_style),
    ]
    return [prefix + f"<path {' '.join(attr for attr in attrs if attr)} />"]


def _rect_to_svg(shape: RectShape, *, include_style: bool = True) -> str:
    attrs = [
        f'id="{escape(shape.id)}"',
        f'x="{_fmt(shape.x)}"',
        f'y="{_fmt(shape.y)}"',
        f'width="{_fmt(shape.width)}"',
        f'height="{_fmt(shape.height)}"',
        f'rx="{_fmt(shape.rx)}"' if shape.rx else "",
        f'ry="{_fmt(shape.ry)}"' if shape.ry else "",
        *(_style_attrs(shape) if include_style else _clip_style_attrs()),
        *_common_attrs(shape, include_clip=include_style),
    ]
    return f"<rect {' '.join(attr for attr in attrs if attr)} />"


def _ellipse_to_svg(shape: EllipseShape, *, include_style: bool = True) -> str:
    attrs = [
        f'id="{escape(shape.id)}"',
        f'cx="{_fmt(shape.cx)}"',
        f'cy="{_fmt(shape.cy)}"',
        f'rx="{_fmt(shape.rx)}"',
        f'ry="{_fmt(shape.ry)}"',
        *(_style_attrs(shape) if include_style else _clip_style_attrs()),
        *_common_attrs(shape, include_clip=include_style),
    ]
    return f"<ellipse {' '.join(attr for attr in attrs if attr)} />"


def _polygon_to_svg(
    shape: PolygonShape | StarShape,
    *,
    points: list[list[float]] | None = None,
    include_style: bool = True,
) -> str:
    polygon_points = points if points is not None else shape.points
    point_text = " ".join(f"{_fmt(point[0])},{_fmt(point[1])}" for point in polygon_points)
    attrs = [
        f'id="{escape(shape.id)}"',
        f'points="{escape(point_text)}"',
        *(_style_attrs(shape) if include_style else _clip_style_attrs()),
        *_common_attrs(shape, include_clip=include_style),
    ]
    return f"<polygon {' '.join(attr for attr in attrs if attr)} />"


def _star_points(shape: StarShape) -> list[list[float]]:
    inner_radius = shape.inner_radius if shape.inner_radius is not None else shape.outer_radius * 0.5
    angle_offset = math.radians(shape.rotation) - math.pi / 2
    points: list[list[float]] = []
    for index in range(shape.points * 2):
        radius = shape.outer_radius if index % 2 == 0 else inner_radius
        angle = angle_offset + index * math.pi / shape.points
        points.append([shape.cx + math.cos(angle) * radius, shape.cy + math.sin(angle) * radius])
    return points


def _commands_to_d(commands: list[PathCommand], *, closed: bool) -> str:
    parts: list[str] = []
    has_close = False
    for command in commands:
        if command.command == "Z":
            has_close = True
            parts.append("Z")
        else:
            values = " ".join(_fmt(value) for value in command.values)
            parts.append(f"{command.command} {values}")
    if closed and not has_close:
        parts.append("Z")
    return " ".join(parts)


def _stroke_attrs(stroke: Stroke | None) -> str:
    if stroke is None:
        return 'stroke="none"'
    return (
        f'stroke="{escape(stroke.color)}" '
        f'stroke-width="{_fmt(stroke.width)}" '
        f'stroke-linejoin="{stroke.join}" '
        f'stroke-linecap="{stroke.cap}"'
    )


def _style_attrs(shape: LineArtShape) -> list[str]:
    return [
        f'fill="{escape(_fill_value(shape.fill))}"',
        _stroke_attrs(shape.stroke),
    ]


def _clip_style_attrs() -> list[str]:
    return ['fill="#000000"', 'stroke="none"']


def _common_attrs(shape: LineArtShape, *, include_clip: bool) -> list[str]:
    attrs = [
        f'transform="{escape(_transform_value(shape.transform))}"' if shape.transform is not None else "",
        f'opacity="{_fmt(shape.opacity)}"' if shape.opacity is not None else "",
    ]
    if include_clip and shape.clip_path is not None:
        attrs.append(f'clip-path="url(#{escape(shape.clip_path)})"')
    return attrs


def _transform_value(transform: Transform) -> str:
    parts: list[str] = []
    if transform.translate is not None:
        parts.append(f"translate({_fmt(transform.translate[0])} {_fmt(transform.translate[1])})")
    if transform.rotate is not None:
        if transform.rotate_origin is None:
            parts.append(f"rotate({_fmt(transform.rotate)})")
        else:
            parts.append(
                "rotate("
                f"{_fmt(transform.rotate)} {_fmt(transform.rotate_origin[0])} {_fmt(transform.rotate_origin[1])}"
                ")"
            )
    if transform.scale is not None:
        if isinstance(transform.scale, float):
            parts.append(f"scale({_fmt(transform.scale)})")
        else:
            parts.append(f"scale({_fmt(transform.scale[0])} {_fmt(transform.scale[1])})")
    return " ".join(parts)


def _fill_value(fill: object) -> str:
    if fill is None or fill == "none":
        return "none"
    if isinstance(fill, GradientFill):
        return f"url(#{fill.ref})"
    return fill.color


def _fmt(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text or "0"
