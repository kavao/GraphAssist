"""LineArt SVG export."""

from __future__ import annotations

from html import escape
from pathlib import Path

from graphassist.engine.lineart.smooth import catmull_rom_to_commands
from graphassist.schema.lineart import LineArtDocument, LineArtShape, PathCommand, PathShape, SmoothPathShape, Stroke


def export_svg(document: LineArtDocument) -> str:
    attrs = [
        'xmlns="http://www.w3.org/2000/svg"',
        f'width="{document.canvas.width}"',
        f'height="{document.canvas.height}"',
        f'viewBox="0 0 {document.canvas.width} {document.canvas.height}"',
    ]
    lines = [f"<svg {' '.join(attrs)}>"]
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
            lines.append(f"    {_shape_to_svg(shape)}")
        lines.append("  </g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def write_svg(document: LineArtDocument, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(export_svg(document), encoding="utf-8")
    return output


def _shape_to_svg(shape: LineArtShape) -> str:
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
        f'fill="{escape(shape.fill.color if shape.fill else "none")}"',
        _stroke_attrs(shape.stroke),
    ]
    return f"<path {' '.join(attr for attr in attrs if attr)} />"


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


def _fmt(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text or "0"
