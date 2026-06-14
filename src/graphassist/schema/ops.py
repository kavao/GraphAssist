"""ImageJob operation モデル。"""

from __future__ import annotations

from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

from graphassist.engine.colors import is_allowed_color
from graphassist.schema.paths import resolve_font, resolve_input


def _validate_color(value: str) -> str:
    if not is_allowed_color(value):
        raise ValueError(f"color is not allowed: {value}")
    return value.lower() if not value.startswith("#") else value


class ResizeOp(BaseModel):
    type: Literal["resize"]
    width: Optional[int] = Field(default=None, ge=1, le=8000)
    height: Optional[int] = Field(default=None, ge=1, le=8000)
    long_edge: Optional[int] = Field(default=None, ge=1, le=8000)


class CropOp(BaseModel):
    type: Literal["crop"]
    width: int = Field(ge=1, le=8000)
    height: int = Field(ge=1, le=8000)
    x: int = Field(ge=0, le=8000)
    y: int = Field(ge=0, le=8000)


class ExtendOp(BaseModel):
    type: Literal["extend"]
    left: int = Field(default=0, ge=0, le=2000)
    right: int = Field(default=0, ge=0, le=2000)
    top: int = Field(default=0, ge=0, le=2000)
    bottom: int = Field(default=0, ge=0, le=2000)
    fill: str = "transparent"

    @field_validator("fill")
    @classmethod
    def validate_fill(cls, value: str) -> str:
        return _validate_color(value)


class RotateOp(BaseModel):
    type: Literal["rotate"]
    degrees: int = Field(ge=-360, le=360)
    fill: str = "transparent"

    @field_validator("fill")
    @classmethod
    def validate_fill(cls, value: str) -> str:
        return _validate_color(value)


class BorderOp(BaseModel):
    type: Literal["border"]
    size: int = Field(ge=1, le=1000)
    color: str

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        return _validate_color(value)


class CompositeOp(BaseModel):
    type: Literal["composite"]
    overlay: str
    x: int = Field(default=0, ge=-8000, le=8000)
    y: int = Field(default=0, ge=-8000, le=8000)
    anchor: Literal["top_left", "center"] = "top_left"

    @field_validator("overlay")
    @classmethod
    def validate_overlay(cls, value: str) -> str:
        resolve_input(value, must_exist=False)
        return value


class TextOp(BaseModel):
    type: Literal["text"]
    content: str = Field(min_length=1, max_length=2000)
    font: str
    size: int = Field(ge=1, le=500)
    color: str = "white"
    x: int = Field(default=0, ge=-8000, le=8000)
    y: int = Field(default=0, ge=-8000, le=8000)
    stroke_color: str | None = None
    stroke_width: int = Field(default=0, ge=0, le=50)

    @field_validator("font")
    @classmethod
    def validate_font(cls, value: str) -> str:
        resolve_font(value, must_exist=False)
        return value

    @field_validator("color", "stroke_color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_color(value)


class TrimOp(BaseModel):
    type: Literal["trim"]
    background: Literal["transparent", "white", "black"] = "transparent"
    padding: int = Field(default=0, ge=0, le=500)
    tolerance: int = Field(default=0, ge=0, le=255)


class FlattenOp(BaseModel):
    type: Literal["flatten"]
    background: str = "white"

    @field_validator("background")
    @classmethod
    def validate_background(cls, value: str) -> str:
        normalized = _validate_color(value)
        if normalized == "transparent":
            raise ValueError("flatten background cannot be transparent")
        return normalized


Operation = Annotated[
    Union[
        ResizeOp,
        CropOp,
        ExtendOp,
        RotateOp,
        BorderOp,
        CompositeOp,
        TextOp,
        TrimOp,
        FlattenOp,
    ],
    Field(discriminator="type"),
]
