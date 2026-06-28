"""FontOutline JSON schema."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator

from graphassist.schema.lineart import PathCommand, SolidFill, Stroke

Point = Annotated[list[float], Field(min_length=2, max_length=2)]


class FontOutlineMetrics(BaseModel):
    units_per_em: int = Field(gt=0)
    ascender: float
    descender: float
    width: float = Field(ge=0)
    height: float = Field(ge=0)


class FontGlyphOutline(BaseModel):
    char: str = Field(min_length=1, max_length=1)
    glyph_name: str
    origin: Point
    advance: float = Field(ge=0)
    commands: list[PathCommand]

    @field_validator("commands", mode="before")
    @classmethod
    def parse_commands(cls, value: object) -> object:
        if isinstance(value, list):
            return [PathCommand.from_raw(item) if isinstance(item, list) else item for item in value]
        return value

    @field_serializer("commands")
    def serialize_commands(self, commands: list[PathCommand]) -> list[list[object]]:
        return [command.to_raw() for command in commands]

    @model_validator(mode="after")
    def validate_commands(self) -> FontGlyphOutline:
        if not self.commands:
            raise ValueError("glyph commands must not be empty")
        if self.commands[0].command != "M":
            raise ValueError("glyph path must start with M")
        return self


class FontOutlineDocument(BaseModel):
    version: Literal["1.0"]
    source_text: str = Field(min_length=1)
    font: str
    font_size: float = Field(gt=0)
    layout: Literal["horizontal"] = "horizontal"
    metrics: FontOutlineMetrics
    glyphs: list[FontGlyphOutline]
    default_fill: SolidFill = Field(default_factory=lambda: SolidFill(color="#111111"))
    default_stroke: Stroke | None = None

    @model_validator(mode="after")
    def validate_glyphs(self) -> FontOutlineDocument:
        if not self.glyphs:
            raise ValueError("FontOutline requires at least one glyph")
        return self
