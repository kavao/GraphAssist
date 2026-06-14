"""MosaicArt（CharGrid）スキーマ。"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
MAX_PALETTE_SIZE = 32
DEFAULT_MAX_COLORS = 16


class MosaicMeta(BaseModel):
    title: str | None = None
    source: str | None = None


class MosaicArt(BaseModel):
    version: Literal["1.0"]
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    transparent: str = "."
    palette: dict[str, str]
    rows: list[str]
    meta: MosaicMeta | None = None

    @field_validator("transparent")
    @classmethod
    def validate_transparent(cls, value: str) -> str:
        if len(value) != 1 or not value.isprintable() or value.isspace():
            raise ValueError("transparent must be a single printable non-space character")
        return value

    @field_validator("palette")
    @classmethod
    def validate_palette(cls, value: dict[str, str]) -> dict[str, str]:
        if not value:
            raise ValueError("palette must not be empty")
        if len(value) > MAX_PALETTE_SIZE:
            raise ValueError(f"palette must have at most {MAX_PALETTE_SIZE} entries")
        for key, color in value.items():
            if len(key) != 1 or not key.isprintable() or key.isspace():
                raise ValueError(f"palette key must be a single printable character: {key!r}")
            if not HEX_COLOR_RE.match(color):
                raise ValueError(f"invalid color for {key!r}: {color}")
        return value

    @model_validator(mode="after")
    def validate_grid(self) -> MosaicArt:
        if self.transparent in self.palette:
            raise ValueError("transparent character must not appear in palette keys")
        if len(self.rows) != self.height:
            raise ValueError(f"rows length {len(self.rows)} != height {self.height}")
        for index, row in enumerate(self.rows):
            if len(row) != self.width:
                raise ValueError(f"row {index} length {len(row)} != width {self.width}")
            for char in row:
                if char != self.transparent and char not in self.palette:
                    raise ValueError(f"unknown character {char!r} in row {index}")
        return self


def parse_hex_color(value: str) -> tuple[int, int, int, int]:
    match = HEX_COLOR_RE.match(value)
    if not match:
        raise ValueError(f"invalid hex color: {value}")
    hex_body = match.group(1)
    r = int(hex_body[0:2], 16)
    g = int(hex_body[2:4], 16)
    b = int(hex_body[4:6], 16)
    a = int(hex_body[6:8], 16) if len(hex_body) == 8 else 255
    return (r, g, b, a)


def rgba_to_hex(value: tuple[int, int, int, int]) -> str:
    r, g, b, a = value
    if a == 255:
        return f"#{r:02x}{g:02x}{b:02x}"
    return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
