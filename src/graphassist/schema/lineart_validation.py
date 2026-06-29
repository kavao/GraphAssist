"""LineArt validation report schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from graphassist.schema.lineart import Severity

ValidationResult = Literal["passed", "failed", "warning_only"]


class ValidationSource(BaseModel):
    document_id: str
    input_path: str


class ValidationSummary(BaseModel):
    errors: int = 0
    warnings: int = 0
    info: int = 0
    geometries: int = 0


class RepairHint(BaseModel):
    action: str
    target: str | None = None
    anchor: str | None = None
    toward: str | None = None
    delta: list[float] | None = None
    constraints: dict[str, object] | None = None


class ValidationIssue(BaseModel):
    issue_id: str
    type: str
    severity: Severity
    object_ids: list[str]
    position: list[float] | None = None
    metric: dict[str, object] = Field(default_factory=dict)
    message: str
    repair_hint: RepairHint | None = None


class ValidationReport(BaseModel):
    version: Literal["0.1"] = "0.1"
    validation_result: ValidationResult
    source: ValidationSource
    summary: ValidationSummary
    issues: list[ValidationIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_result_matches_summary(self) -> ValidationReport:
        if self.summary.errors > 0 and self.validation_result != "failed":
            raise ValueError("validation_result must be failed when errors are present")
        if self.summary.errors == 0 and self.summary.warnings > 0 and self.validation_result != "warning_only":
            raise ValueError("validation_result must be warning_only when only warnings are present")
        if self.summary.errors == 0 and self.summary.warnings == 0 and self.validation_result != "passed":
            raise ValueError("validation_result must be passed when no issues are present")
        return self

