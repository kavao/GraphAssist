"""Batch manifest — 1 JSON に複数命令。"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from graphassist.schema.job import ImageJob
from graphassist.schema.mosaic import MosaicArt
from graphassist.schema.ops import Operation
from graphassist.schema.paths import (
    resolve_input,
    resolve_mosaic_json,
    resolve_mosaic_output,
    resolve_output,
)


class JobCommand(BaseModel):
    type: Literal["job"]
    input: str
    output: str
    operations: list[Operation]

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str) -> str:
        resolve_input(value, must_exist=False)
        return value

    @field_validator("output")
    @classmethod
    def validate_output(cls, value: str) -> str:
        resolve_output(value)
        return value

    def to_image_job(self) -> ImageJob:
        return ImageJob(
            version="1.0",
            input=self.input,
            output=self.output,
            operations=self.operations,
        )


class MosaicDecodeCommand(BaseModel):
    type: Literal["mosaic.decode"]
    output: str
    input: str | None = None
    art: MosaicArt | None = None
    cell_size: int = Field(default=1, ge=1, le=256)
    format: Literal["png", "webp"] = "png"
    quality: int = Field(default=85, ge=1, le=100)

    @field_validator("output")
    @classmethod
    def validate_output(cls, value: str) -> str:
        resolve_output(value)
        return value

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str | None) -> str | None:
        if value is None:
            return None
        resolve_mosaic_json(value, must_exist=False)
        return value

    @model_validator(mode="after")
    def validate_source(self) -> MosaicDecodeCommand:
        if (self.input is None) == (self.art is None):
            raise ValueError("mosaic.decode requires exactly one of 'input' or 'art'")
        return self


class MosaicEncodeCommand(BaseModel):
    type: Literal["mosaic.encode"]
    input: str
    output: str
    grid: str
    max_colors: int = Field(default=16, ge=1, le=32)
    transparent: str = "."
    alpha_threshold: int = Field(default=128, ge=0, le=255)

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str) -> str:
        resolve_input(value, must_exist=False)
        return value

    @field_validator("output")
    @classmethod
    def validate_output(cls, value: str) -> str:
        resolve_mosaic_output(value)
        return value


class MosaicExportCommand(BaseModel):
    type: Literal["mosaic.export"]
    input: str
    format: Literal["js", "json"] = "js"
    output: str | None = None
    name: str | None = None

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str) -> str:
        resolve_mosaic_json(value, must_exist=False)
        return value

    @field_validator("output")
    @classmethod
    def validate_output(cls, value: str | None) -> str | None:
        if value is None:
            return None
        resolve_mosaic_output(value)
        return value


BatchCommand = Annotated[
    Union[JobCommand, MosaicDecodeCommand, MosaicEncodeCommand, MosaicExportCommand],
    Field(discriminator="type"),
]


class BatchManifest(BaseModel):
    version: Literal["1.0"]
    commands: list[BatchCommand] = Field(min_length=1)


def is_batch_manifest(data: dict) -> bool:
    return "commands" in data
