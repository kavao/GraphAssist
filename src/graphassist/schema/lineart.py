"""LineArt JSON schema."""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
SAFE_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")

LineArtRole = Literal[
    "container",
    "node",
    "connector",
    "label",
    "annotation",
    "glyph",
    "decorative",
    "background",
]

Severity = Literal["error", "warning", "info"]
PathCommandName = Literal["M", "L", "Q", "C", "Z"]


class LineArtCanvas(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    background: str = "transparent"

    @field_validator("background")
    @classmethod
    def validate_background(cls, value: str) -> str:
        if value == "transparent" or HEX_COLOR_RE.match(value):
            return value
        raise ValueError("background must be transparent or #RRGGBB/#RRGGBBAA")


class SolidFill(BaseModel):
    type: Literal["solid"] = "solid"
    color: str

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if HEX_COLOR_RE.match(value):
            return value
        raise ValueError("fill color must be #RRGGBB or #RRGGBBAA")


class GradientFill(BaseModel):
    type: Literal["gradient"] = "gradient"
    ref: str

    @field_validator("ref")
    @classmethod
    def validate_ref(cls, value: str) -> str:
        if SAFE_ID_RE.match(value):
            return value
        raise ValueError("gradient ref must start with a letter and contain letters, digits, _ or -")


LineArtFill = Literal["none"] | SolidFill | GradientFill


class Stroke(BaseModel):
    color: str
    width: float = Field(gt=0)
    join: Literal["miter", "round", "bevel"] = "round"
    cap: Literal["butt", "round", "square"] = "round"

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if HEX_COLOR_RE.match(value) or _is_gradient_url(value):
            return value
        raise ValueError("stroke color must be #RRGGBB/#RRGGBBAA or url(#gradient_id)")


class NearExpectation(BaseModel):
    target: str
    max_distance: float = Field(ge=0)


class ValidationExpected(BaseModel):
    inside: str | None = None
    near: NearExpectation | None = None
    touches: list[str] | None = None
    no_intersections: bool | None = None


class ShapeValidation(BaseModel):
    expected: ValidationExpected | dict[str, object] = Field(default_factory=dict)
    severity: Severity = "warning"


class ConnectsTo(BaseModel):
    from_: str = Field(alias="from")
    to: str

    model_config = {"populate_by_name": True}


class LineArtMetadata(BaseModel):
    role: LineArtRole | None = None
    name: str | None = None
    label: str | None = None
    tags: list[str] = Field(default_factory=list)
    description: str | None = None
    locked: bool = False
    visible: bool = True
    container_id: str | None = None
    connects_to: ConnectsTo | None = None
    allow_overlap: bool | None = None
    expected_position: dict[str, object] | None = None
    validation: ShapeValidation | None = None


Point = Annotated[list[float], Field(min_length=2, max_length=2)]


class Transform(BaseModel):
    translate: Point | None = None
    rotate: float | None = None
    rotate_origin: Point | None = None
    scale: float | Point | None = None

    @field_validator("scale")
    @classmethod
    def validate_scale(cls, value: float | Point | None) -> float | Point | None:
        if value is None:
            return value
        if isinstance(value, int | float):
            if value <= 0:
                raise ValueError("scale must be greater than 0")
            return float(value)
        if len(value) != 2 or value[0] <= 0 or value[1] <= 0:
            raise ValueError("scale point values must be greater than 0")
        return value


class ShapeBase(LineArtMetadata):
    id: str
    fill: LineArtFill | None = None
    stroke: Stroke | None = None
    transform: Transform | None = None
    opacity: float | None = Field(default=None, ge=0, le=1)
    clip_path: str | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if SAFE_ID_RE.match(value):
            return value
        raise ValueError("id must start with a letter and contain letters, digits, _ or -")

    @field_validator("clip_path")
    @classmethod
    def validate_clip_path(cls, value: str | None) -> str | None:
        if value is None or SAFE_ID_RE.match(value):
            return value
        raise ValueError("clip_path must start with a letter and contain letters, digits, _ or -")


class PathCommand(BaseModel):
    command: PathCommandName
    values: list[float] = Field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: list[object]) -> PathCommand:
        if not raw:
            raise ValueError("path command must not be empty")
        command = raw[0]
        if not isinstance(command, str):
            raise ValueError("path command name must be a string")
        return cls(command=command, values=[float(value) for value in raw[1:]])

    @model_validator(mode="after")
    def validate_value_count(self) -> PathCommand:
        expected = {"M": 2, "L": 2, "Q": 4, "C": 6, "Z": 0}[self.command]
        if len(self.values) != expected:
            raise ValueError(f"{self.command} command requires {expected} numeric values")
        return self

    def to_raw(self) -> list[object]:
        return [self.command, *self.values]


class PathShape(ShapeBase):
    type: Literal["path"]
    commands: list[PathCommand]
    closed: bool = False

    @field_validator("commands", mode="before")
    @classmethod
    def parse_commands(cls, value: object) -> object:
        if isinstance(value, list):
            return [PathCommand.from_raw(item) if isinstance(item, list) else item for item in value]
        return value

    @model_validator(mode="after")
    def validate_commands(self) -> PathShape:
        if not self.commands:
            raise ValueError("path commands must not be empty")
        if self.commands[0].command != "M":
            raise ValueError("path must start with M")
        return self


class SmoothPathShape(ShapeBase):
    type: Literal["smooth_path"]
    points: list[Point]
    interpolation: Literal["catmull_rom"] = "catmull_rom"
    closed: bool = False

    @field_validator("points")
    @classmethod
    def validate_points(cls, value: list[Point]) -> list[Point]:
        if len(value) < 2:
            raise ValueError("smooth_path requires at least 2 points")
        return value


class RectShape(ShapeBase):
    type: Literal["rect"]
    x: float
    y: float
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    rx: float = Field(default=0, ge=0)
    ry: float = Field(default=0, ge=0)


class EllipseShape(ShapeBase):
    type: Literal["ellipse"]
    cx: float
    cy: float
    rx: float = Field(gt=0)
    ry: float = Field(gt=0)


class PolygonShape(ShapeBase):
    type: Literal["polygon"]
    points: list[Point]

    @field_validator("points")
    @classmethod
    def validate_points(cls, value: list[Point]) -> list[Point]:
        if len(value) < 3:
            raise ValueError("polygon requires at least 3 points")
        return value


class StarShape(ShapeBase):
    type: Literal["star"]
    cx: float
    cy: float
    points: int = Field(ge=3, le=64)
    outer_radius: float = Field(gt=0)
    inner_radius: float | None = Field(default=None, gt=0)
    rotation: float = 0

    @model_validator(mode="after")
    def validate_inner_radius(self) -> StarShape:
        if self.inner_radius is not None and self.inner_radius >= self.outer_radius:
            raise ValueError("inner_radius must be smaller than outer_radius")
        return self


ClipShape = Annotated[
    PathShape | SmoothPathShape | RectShape | EllipseShape | PolygonShape | StarShape,
    Field(discriminator="type"),
]


class GroupShape(ShapeBase):
    type: Literal["group"]
    shapes: list["LineArtShape"] = Field(default_factory=list)

    @field_validator("shapes")
    @classmethod
    def validate_shapes(cls, value: list["LineArtShape"]) -> list["LineArtShape"]:
        if not value:
            raise ValueError("group requires at least one child shape")
        return value


LineArtShape = Annotated[
    PathShape | SmoothPathShape | RectShape | EllipseShape | PolygonShape | StarShape | GroupShape,
    Field(discriminator="type"),
]


class LineArtLayer(BaseModel):
    id: str
    shapes: list[LineArtShape] = Field(default_factory=list)
    visible: bool = True

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if SAFE_ID_RE.match(value):
            return value
        raise ValueError("layer id must start with a letter and contain letters, digits, _ or -")


class GradientStop(BaseModel):
    offset: float = Field(ge=0, le=1)
    color: str
    opacity: float | None = Field(default=None, ge=0, le=1)

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if HEX_COLOR_RE.match(value):
            return value
        raise ValueError("gradient stop color must be #RRGGBB or #RRGGBBAA")


class LinearGradient(BaseModel):
    type: Literal["linear"]
    from_: Point = Field(alias="from")
    to: Point
    stops: list[GradientStop]
    units: Literal["userSpaceOnUse", "objectBoundingBox"] = "userSpaceOnUse"

    model_config = {"populate_by_name": True}

    @field_validator("stops")
    @classmethod
    def validate_stops(cls, value: list[GradientStop]) -> list[GradientStop]:
        return _validate_gradient_stops(value)


class RadialGradient(BaseModel):
    type: Literal["radial"]
    center: Point
    radius: float = Field(gt=0)
    focal: Point | None = None
    stops: list[GradientStop]
    units: Literal["userSpaceOnUse", "objectBoundingBox"] = "userSpaceOnUse"

    @field_validator("stops")
    @classmethod
    def validate_stops(cls, value: list[GradientStop]) -> list[GradientStop]:
        return _validate_gradient_stops(value)


LineArtGradient = Annotated[LinearGradient | RadialGradient, Field(discriminator="type")]


class ClipPathDefinition(BaseModel):
    shapes: list[ClipShape]

    @field_validator("shapes")
    @classmethod
    def validate_shapes(cls, value: list[ClipShape]) -> list[ClipShape]:
        if not value:
            raise ValueError("clip_path requires at least one shape")
        return value


class LineArtDefinitions(BaseModel):
    gradients: dict[str, LineArtGradient] = Field(default_factory=dict)
    clip_paths: dict[str, ClipPathDefinition] = Field(default_factory=dict)

    @field_validator("gradients")
    @classmethod
    def validate_gradient_ids(cls, value: dict[str, LineArtGradient]) -> dict[str, LineArtGradient]:
        for gradient_id in value:
            if not SAFE_ID_RE.match(gradient_id):
                raise ValueError("gradient id must start with a letter and contain letters, digits, _ or -")
        return value

    @field_validator("clip_paths")
    @classmethod
    def validate_clip_path_ids(cls, value: dict[str, ClipPathDefinition]) -> dict[str, ClipPathDefinition]:
        for clip_path_id in value:
            if not SAFE_ID_RE.match(clip_path_id):
                raise ValueError("clip_path id must start with a letter and contain letters, digits, _ or -")
        return value


class LineArtDocument(BaseModel):
    version: Literal["1.0"]
    canvas: LineArtCanvas
    definitions: LineArtDefinitions = Field(default_factory=LineArtDefinitions)
    layers: list[LineArtLayer]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> LineArtDocument:
        seen: set[str] = set()
        gradient_ids = set(self.definitions.gradients)
        clip_path_ids = set(self.definitions.clip_paths)
        for layer in self.layers:
            if layer.id in seen:
                raise ValueError(f"duplicate id: {layer.id}")
            seen.add(layer.id)
            for shape in layer.shapes:
                _validate_shape_refs(shape, seen, gradient_ids, clip_path_ids)
        return self


def _validate_gradient_stops(stops: list[GradientStop]) -> list[GradientStop]:
    if len(stops) < 2:
        raise ValueError("gradient requires at least two stops")
    offsets = [stop.offset for stop in stops]
    if offsets != sorted(offsets):
        raise ValueError("gradient stop offsets must be sorted")
    return stops


def _validate_shape_refs(
    shape: LineArtShape,
    seen: set[str],
    gradient_ids: set[str],
    clip_path_ids: set[str],
) -> None:
    if shape.id in seen:
        raise ValueError(f"duplicate id: {shape.id}")
    seen.add(shape.id)
    _validate_shape_gradient_refs(shape, gradient_ids)
    if shape.clip_path is not None and shape.clip_path not in clip_path_ids:
        raise ValueError(f"undefined clip_path: {shape.clip_path}")
    if isinstance(shape, GroupShape):
        for child in shape.shapes:
            _validate_shape_refs(child, seen, gradient_ids, clip_path_ids)


def _validate_shape_gradient_refs(shape: LineArtShape, gradient_ids: set[str]) -> None:
    if isinstance(shape.fill, GradientFill) and shape.fill.ref not in gradient_ids:
        raise ValueError(f"undefined gradient: {shape.fill.ref}")
    if shape.stroke is not None and _is_gradient_url(shape.stroke.color):
        ref = shape.stroke.color[5:-1]
        if ref not in gradient_ids:
            raise ValueError(f"undefined gradient: {ref}")


def _is_gradient_url(value: str) -> bool:
    return value.startswith("url(#") and value.endswith(")") and SAFE_ID_RE.match(value[5:-1]) is not None
