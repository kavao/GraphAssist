"""ImageJob モデル。"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

from graphassist.engine.catalog_resolve import resolve_catalog_asset
from graphassist.schema.catalog import validate_catalog_id
from graphassist.schema.ops import Operation
from graphassist.schema.paths import project_root, resolve_input, resolve_output


class ImageJob(BaseModel):
    version: Literal["1.0"]
    input: str | None = None
    input_asset: str | None = None
    output: str
    operations: list[Operation]

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str | None) -> str | None:
        if value is None:
            return None
        resolve_input(value, must_exist=False)
        return value

    @field_validator("input_asset")
    @classmethod
    def validate_input_asset(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_catalog_id(value)

    @field_validator("output")
    @classmethod
    def validate_output(cls, value: str) -> str:
        resolve_output(value)
        return value

    @model_validator(mode="after")
    def validate_input_source(self) -> ImageJob:
        if (self.input is None) == (self.input_asset is None):
            raise ValueError("ImageJob requires exactly one of 'input' or 'input_asset'")
        return self

    @property
    def display_input(self) -> str:
        if self.input_asset:
            return f"asset:{self.input_asset}"
        assert self.input is not None
        return self.input

    def resolved_input(self, *, root: Path | None = None, must_exist: bool = True) -> Path:
        base = root or project_root()
        if self.input_asset:
            return resolve_catalog_asset(
                self.input_asset,
                root=base,
                must_exist=must_exist,
                auto_materialize=must_exist,
            )
        assert self.input is not None
        return resolve_input(self.input, root=base, must_exist=must_exist)

    def resolved_output(self):
        return resolve_output(self.output)
