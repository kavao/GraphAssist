"""ImageJob モデル。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator

from tools.graphassist.schema.ops import Operation
from tools.graphassist.schema.paths import resolve_input, resolve_output


class ImageJob(BaseModel):
    version: Literal["1.0"]
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

    def resolved_input(self, *, must_exist: bool = True):
        return resolve_input(self.input, must_exist=must_exist)

    def resolved_output(self):
        return resolve_output(self.output)
