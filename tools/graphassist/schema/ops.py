"""ImageJob operation モデル。"""

from __future__ import annotations

from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

from tools.graphassist.engine.colors import ALLOWED_COLOR_NAMES
from tools.graphassist.schema.paths import resolve_input


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
        if value.lower() not in ALLOWED_COLOR_NAMES:
            raise ValueError(f"color is not allowed: {value}")
        return value.lower()


class RotateOp(BaseModel):
    type: Literal["rotate"]
    degrees: int = Field(ge=-360, le=360)
    fill: str = "transparent"

    @field_validator("fill")
    @classmethod
    def validate_fill(cls, value: str) -> str:
        if value.lower() not in ALLOWED_COLOR_NAMES:
            raise ValueError(f"color is not allowed: {value}")
        return value.lower()


class BorderOp(BaseModel):
    type: Literal["border"]
    size: int = Field(ge=1, le=1000)
    color: str

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if value.lower() not in ALLOWED_COLOR_NAMES:
            raise ValueError(f"color is not allowed: {value}")
        return value.lower()


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


Operation = Annotated[
    Union[ResizeOp, CropOp, ExtendOp, RotateOp, BorderOp, CompositeOp],
    Field(discriminator="type"),
]
