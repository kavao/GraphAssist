"""Convert FontOutline documents into LineArt documents."""

from __future__ import annotations

from graphassist.schema.font_outline import FontGlyphOutline, FontOutlineDocument
from graphassist.schema.lineart import (
    GroupShape,
    LineArtCanvas,
    LineArtDefinitions,
    LineArtDocument,
    LineArtLayer,
    PathCommand,
    PathShape,
    SolidFill,
    Stroke,
)


def font_outline_to_lineart(document: FontOutlineDocument, *, padding: float = 16.0) -> LineArtDocument:
    y_offset = padding + document.metrics.ascender
    shapes = [
        _glyph_to_path(
            glyph,
            y_offset=y_offset,
            padding=padding,
            fill=document.default_fill,
            stroke=document.default_stroke,
        )
        for glyph in document.glyphs
    ]
    group = GroupShape(
        id="text_outline",
        type="group",
        role="label",
        label=document.source_text,
        tags=["fontvector", "outlined_text"],
        shapes=shapes,
    )
    return LineArtDocument(
        version="1.0",
        canvas=LineArtCanvas(
            width=max(1, int(round(document.metrics.width + padding * 2))),
            height=max(1, int(round(document.metrics.height + padding * 2))),
            background="transparent",
        ),
        definitions=LineArtDefinitions(),
        layers=[LineArtLayer(id="font_outline", shapes=[group])],
    )


def lineart_document_to_json_payload(document: LineArtDocument) -> dict[str, object]:
    return {
        "version": document.version,
        "canvas": document.canvas.model_dump(mode="json"),
        "definitions": document.definitions.model_dump(mode="json"),
        "layers": [
            {
                "id": layer.id,
                "visible": layer.visible,
                "shapes": [_shape_to_payload(shape) for shape in layer.shapes],
            }
            for layer in document.layers
        ],
    }


def _glyph_to_path(
    glyph: FontGlyphOutline,
    *,
    y_offset: float,
    padding: float,
    fill: SolidFill,
    stroke: Stroke | None,
) -> PathShape:
    return PathShape(
        id=_glyph_id(glyph),
        type="path",
        role="glyph",
        name=glyph.char,
        tags=["fontvector", "glyph"],
        fill=fill,
        stroke=stroke,
        commands=[_shift_command(command, x_offset=padding, y_offset=y_offset) for command in glyph.commands],
        closed=True,
    )


def _shift_command(command: PathCommand, *, x_offset: float, y_offset: float) -> PathCommand:
    values = command.values.copy()
    for index in range(0, len(values), 2):
        values[index] = round(values[index] + x_offset, 4)
        values[index + 1] = round(values[index + 1] + y_offset, 4)
    return PathCommand(command=command.command, values=values)


def _glyph_id(glyph: FontGlyphOutline) -> str:
    codepoint = ord(glyph.char)
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in glyph.glyph_name)
    if not safe_name or not safe_name[0].isalpha():
        safe_name = f"glyph_{safe_name}"
    return f"{safe_name}_{codepoint:04X}"


def _shape_to_payload(shape) -> dict[str, object]:
    if isinstance(shape, GroupShape):
        payload = _base_payload(shape)
        payload["type"] = "group"
        payload["shapes"] = [_shape_to_payload(child) for child in shape.shapes]
        return payload
    if isinstance(shape, PathShape):
        payload = _base_payload(shape)
        payload["type"] = "path"
        payload["commands"] = [command.to_raw() for command in shape.commands]
        payload["closed"] = shape.closed
        return payload
    raise TypeError(f"unsupported FontVector LineArt shape: {type(shape)!r}")


def _base_payload(shape) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": shape.id,
        "role": shape.role,
        "tags": shape.tags,
    }
    if shape.name is not None:
        payload["name"] = shape.name
    if shape.label is not None:
        payload["label"] = shape.label
    if shape.fill is not None:
        payload["fill"] = shape.fill.model_dump(mode="json") if hasattr(shape.fill, "model_dump") else shape.fill
    if shape.stroke is not None:
        payload["stroke"] = shape.stroke.model_dump(mode="json")
    return payload
