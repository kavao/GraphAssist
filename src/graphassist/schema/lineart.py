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


class Stroke(BaseModel):
    color: str
    width: float = Field(gt=0)
    join: Literal["miter", "round", "bevel"] = "round"
    cap: Literal["butt", "round", "square"] = "round"

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if HEX_COLOR_RE.match(value):
            return value
        raise ValueError("stroke color must be #RRGGBB or #RRGGBBAA")


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


class ShapeBase(LineArtMetadata):
    id: str
    fill: SolidFill | None = None
    stroke: Stroke | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if SAFE_ID_RE.match(value):
            return value
        raise ValueError("id must start with a letter and contain letters, digits, _ or -")


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


Point = Annotated[list[float], Field(min_length=2, max_length=2)]


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


LineArtShape = Annotated[PathShape | SmoothPathShape, Field(discriminator="type")]


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


class LineArtDefinitions(BaseModel):
    gradients: dict[str, object] = Field(default_factory=dict)
    clip_paths: dict[str, object] = Field(default_factory=dict)


class LineArtDocument(BaseModel):
    version: Literal["1.0"]
    canvas: LineArtCanvas
    definitions: LineArtDefinitions = Field(default_factory=LineArtDefinitions)
    layers: list[LineArtLayer]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> LineArtDocument:
        seen: set[str] = set()
        for layer in self.layers:
            if layer.id in seen:
                raise ValueError(f"duplicate id: {layer.id}")
            seen.add(layer.id)
            for shape in layer.shapes:
                if shape.id in seen:
                    raise ValueError(f"duplicate id: {shape.id}")
                seen.add(shape.id)
        return self
