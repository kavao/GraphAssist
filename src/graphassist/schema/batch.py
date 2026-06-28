"""Batch manifest — 1 JSON に複数命令。"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from graphassist.schema.catalog import validate_catalog_id
from graphassist.schema.job import ImageJob
from graphassist.schema.mosaic import MosaicArt
from graphassist.schema.ops import Operation
from graphassist.schema.paths import (
    is_under_output,
    normalize_manifest_path,
    resolve_lineart_input,
    resolve_lineart_output,
    resolve_lineart_raster_output,
    resolve_input,
    resolve_mosaic_json,
    resolve_mosaic_output,
    resolve_output,
)


class JobCommand(BaseModel):
    type: Literal["job"]
    input: str | None = None
    input_asset: str | None = None
    output: str
    operations: list[Operation]

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if is_under_output(value):
            resolve_output(value)
        else:
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
    def validate_input_source(self) -> JobCommand:
        if (self.input is None) == (self.input_asset is None):
            raise ValueError("job command requires exactly one of 'input' or 'input_asset'")
        return self

    def to_image_job(self, *, batch_chained: bool = False) -> ImageJob:
        payload = {
            "version": "1.0",
            "input": self.input,
            "input_asset": self.input_asset,
            "output": self.output,
            "operations": self.operations,
        }
        if batch_chained:
            return ImageJob.model_construct(**payload)
        return ImageJob.model_validate(payload)


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


class LineArtRenderCommand(BaseModel):
    type: Literal["lineart.render"]
    input: str
    output: str
    png_output: str | None = None
    png_width: int | None = Field(default=None, ge=1, le=8000)

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str) -> str:
        resolve_lineart_input(value, must_exist=False)
        return value

    @field_validator("output")
    @classmethod
    def validate_output(cls, value: str) -> str:
        resolve_lineart_output(value)
        return value

    @field_validator("png_output")
    @classmethod
    def validate_png_output(cls, value: str | None) -> str | None:
        if value is None:
            return None
        resolve_lineart_raster_output(value)
        return value


class AssetsMaterializeCommand(BaseModel):
    type: Literal["assets.materialize"]
    ids: list[str] | None = None
    force: bool = False

    @field_validator("ids")
    @classmethod
    def validate_ids(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if not value:
            raise ValueError("ids must be non-empty when provided")
        for asset_id in value:
            validate_catalog_id(asset_id)
        return value


class RoiSpec(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    x: int = Field(ge=0, le=8000)
    y: int = Field(ge=0, le=8000)
    width: int = Field(ge=1, le=8000)
    height: int = Field(ge=1, le=8000)


class AnalyzeCommand(BaseModel):
    type: Literal["analyze"]
    input: str
    compare: str | None = None
    output: str
    max_long_edge: int = Field(default=512, ge=0, le=8000)
    max_colors: int = Field(default=8, ge=1, le=32)
    alpha_threshold: int = Field(default=128, ge=0, le=255)
    threshold_brightness: float = Field(default=0.15, ge=0.0, le=1.0)
    threshold_palette: float = Field(default=0.30, ge=0.0, le=1.0)
    spatial: bool = False
    background: Literal["transparent", "white", "black"] = "transparent"
    tolerance: int = Field(default=0, ge=0, le=255)
    grid_rows: int = Field(default=3, ge=1, le=16)
    grid_cols: int = Field(default=3, ge=1, le=16)
    rois: list[RoiSpec] | None = None
    full_profiles: bool = False

    @field_validator("input", "compare")
    @classmethod
    def validate_input_paths(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if is_under_output(value):
            resolve_output(value)
        else:
            resolve_input(value, must_exist=False)
        return value

    @field_validator("output")
    @classmethod
    def validate_output(cls, value: str) -> str:
        resolve_output(value)
        return value


BatchCommand = Annotated[
    Union[
        JobCommand,
        MosaicDecodeCommand,
        MosaicEncodeCommand,
        MosaicExportCommand,
        LineArtRenderCommand,
        AssetsMaterializeCommand,
        AnalyzeCommand,
    ],
    Field(discriminator="type"),
]


def command_output_path(command: BatchCommand) -> str | None:
    if isinstance(command, MosaicExportCommand):
        return command.output
    if isinstance(command, LineArtRenderCommand):
        return command.png_output or command.output
    if isinstance(command, (JobCommand, MosaicDecodeCommand, MosaicEncodeCommand, AnalyzeCommand)):
        return command.output
    return None


def _require_matches_prev_output(
    index: int,
    path: str,
    prev_output: str | None,
    *,
    label: str,
) -> None:
    if prev_output is None:
        raise ValueError(
            f"commands[{index}]: {label} under generated/ requires a preceding command output"
        )
    if normalize_manifest_path(path) != normalize_manifest_path(prev_output):
        raise ValueError(
            f"commands[{index}]: {label} {path!r} must match "
            f"previous command output {prev_output!r}"
        )


class BatchManifest(BaseModel):
    version: Literal["1.0"]
    commands: list[BatchCommand] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_generated_input_chain(self) -> BatchManifest:
        prior_outputs: set[str] = set()
        prev_output: str | None = None
        for index, command in enumerate(self.commands):
            if isinstance(command, JobCommand) and command.input and is_under_output(command.input):
                _require_matches_prev_output(
                    index, command.input, prev_output, label="job input"
                )
            if isinstance(command, AnalyzeCommand):
                if is_under_output(command.input):
                    _require_matches_prev_output(
                        index, command.input, prev_output, label="analyze input"
                    )
                if command.compare and is_under_output(command.compare):
                    normalized = normalize_manifest_path(command.compare)
                    if normalized not in prior_outputs:
                        raise ValueError(
                            f"commands[{index}]: analyze compare {command.compare!r} must match "
                            "a prior command output under generated/"
                        )
            out = command_output_path(command)
            if out is not None:
                prior_outputs.add(normalize_manifest_path(out))
            prev_output = out
        return self


def is_batch_manifest(data: dict) -> bool:
    return "commands" in data
