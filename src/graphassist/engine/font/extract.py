"""Extract font glyph outlines into FontOutline JSON models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from graphassist.schema.font_outline import FontGlyphOutline, FontOutlineDocument, FontOutlineMetrics
from graphassist.schema.lineart import PathCommand

FONTTOOLS_INSTALL_MESSAGE = "fonttools is required for FontVector. Run: uv sync --extra font"


def extract_font_outline(
    *,
    text: str,
    font_path: Path,
    font_ref: str,
    font_size: float,
    strict: bool = False,
) -> FontOutlineDocument:
    try:
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        from fontTools.ttLib import TTFont
    except ImportError as exc:  # pragma: no cover - exercised without optional extra
        raise RuntimeError(FONTTOOLS_INSTALL_MESSAGE) from exc

    font = TTFont(str(font_path))
    units_per_em = int(font["head"].unitsPerEm)
    scale = font_size / units_per_em
    ascender = float(font["hhea"].ascent) * scale
    descender = float(font["hhea"].descent) * scale
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics

    glyphs: list[FontGlyphOutline] = []
    cursor_x = 0.0
    for char in text:
        glyph_name = cmap.get(ord(char))
        if glyph_name is None:
            if strict:
                raise ValueError(f"glyph not found for U+{ord(char):04X}: {char!r}")
            continue

        pen = DecomposingRecordingPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        commands = _recording_to_commands(pen.value, origin_x=cursor_x, origin_y=0.0, scale=scale)
        advance = float(hmtx.get(glyph_name, (glyph_set[glyph_name].width, 0))[0]) * scale
        if commands:
            glyphs.append(
                FontGlyphOutline(
                    char=char,
                    glyph_name=glyph_name,
                    origin=[_round(cursor_x), 0.0],
                    advance=_round(advance),
                    commands=commands,
                )
            )
        elif strict:
            raise ValueError(f"glyph has no drawable outline: {char!r}")
        cursor_x += advance

    width = cursor_x
    return FontOutlineDocument(
        version="1.0",
        source_text=text,
        font=font_ref.replace("\\", "/"),
        font_size=font_size,
        layout="horizontal",
        metrics=FontOutlineMetrics(
            units_per_em=units_per_em,
            ascender=_round(ascender),
            descender=_round(descender),
            width=_round(width),
            height=_round((float(font["hhea"].ascent) - float(font["hhea"].descent)) * scale),
        ),
        glyphs=glyphs,
    )


def _recording_to_commands(
    recording: list[tuple[str, tuple[Any, ...]]],
    *,
    origin_x: float,
    origin_y: float,
    scale: float,
) -> list[PathCommand]:
    commands: list[PathCommand] = []
    current: tuple[float, float] | None = None
    contour_start: tuple[float, float] | None = None

    for op, points in recording:
        if op == "moveTo":
            point = _transform_point(points[0], origin_x=origin_x, origin_y=origin_y, scale=scale)
            commands.append(PathCommand(command="M", values=list(point)))
            current = point
            contour_start = point
        elif op == "lineTo":
            point = _transform_point(points[0], origin_x=origin_x, origin_y=origin_y, scale=scale)
            commands.append(PathCommand(command="L", values=list(point)))
            current = point
        elif op == "curveTo":
            p1, p2, p3 = [
                _transform_point(point, origin_x=origin_x, origin_y=origin_y, scale=scale)
                for point in points
            ]
            commands.append(PathCommand(command="C", values=[*p1, *p2, *p3]))
            current = p3
        elif op == "qCurveTo":
            if current is None:
                continue
            q_commands, current = _quadratic_commands(
                points,
                current=current,
                origin_x=origin_x,
                origin_y=origin_y,
                scale=scale,
            )
            commands.extend(q_commands)
        elif op in {"closePath", "endPath"}:
            if op == "closePath":
                commands.append(PathCommand(command="Z"))
                current = contour_start

    return commands


def _quadratic_commands(
    points: tuple[Any, ...],
    *,
    current: tuple[float, float],
    origin_x: float,
    origin_y: float,
    scale: float,
) -> tuple[list[PathCommand], tuple[float, float]]:
    if not points:
        return [], current

    transformed = [
        _transform_point(point, origin_x=origin_x, origin_y=origin_y, scale=scale)
        for point in points
        if point is not None
    ]
    if len(transformed) < 2:
        return [], current

    commands: list[PathCommand] = []
    controls = transformed[:-1]
    end = transformed[-1]
    for index, control in enumerate(controls):
        segment_end = _midpoint(control, controls[index + 1]) if index + 1 < len(controls) else end
        commands.append(PathCommand(command="Q", values=[*control, *segment_end]))
        current = segment_end
    return commands, current


def _transform_point(
    point: tuple[float, float],
    *,
    origin_x: float,
    origin_y: float,
    scale: float,
) -> tuple[float, float]:
    x, y = point
    return (_round(float(x) * scale + origin_x), _round(-float(y) * scale + origin_y))


def _midpoint(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (_round((a[0] + b[0]) / 2), _round((a[1] + b[1]) / 2))


def _round(value: float) -> float:
    return round(value, 4)
