"""LineArt validation report schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from graphassist.schema.lineart import Severity

ValidationResult = Literal["passed", "failed", "warning_only"]
RepairMode = Literal["patch_preferred", "targeted_regeneration", "full_regeneration_allowed"]
RepairStopReason = Literal[
    "max_iterations",
    "error_goal_met",
    "warning_goal_met",
    "repeated_issue",
    "blocked_by_scope",
    "continue",
]


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


class RepairLoopStopWhen(BaseModel):
    errors: int = Field(default=0, ge=0)
    allow_warnings: bool = True
    repeated_issue_limit: int = Field(default=2, ge=1)


class RepairScope(BaseModel):
    locked_ids: list[str] = Field(default_factory=list)
    editable_ids: list[str] = Field(default_factory=list)

    @field_validator("locked_ids", "editable_ids")
    @classmethod
    def dedupe_ids(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))

    @model_validator(mode="after")
    def validate_locked_and_editable_do_not_overlap(self) -> RepairScope:
        overlap = set(self.locked_ids) & set(self.editable_ids)
        if overlap:
            raise ValueError(f"locked_ids and editable_ids overlap: {sorted(overlap)}")
        return self


class RepairLoopInputs(BaseModel):
    lineart_document: str
    validation_report: str


class RepairLoopConfig(BaseModel):
    version: Literal["0.1"] = "0.1"
    mode: RepairMode = "patch_preferred"
    max_iterations: int = Field(default=3, ge=1, le=20)
    stop_when: RepairLoopStopWhen = Field(default_factory=RepairLoopStopWhen)
    repair_scope: RepairScope = Field(default_factory=RepairScope)
    inputs: RepairLoopInputs


class RepairLoopDecision(BaseModel):
    should_stop: bool
    reason: RepairStopReason
    editable_issue_ids: list[str] = Field(default_factory=list)
    blocked_issue_ids: list[str] = Field(default_factory=list)


def decide_repair_loop(
    config: RepairLoopConfig,
    report: ValidationReport,
    *,
    iteration: int,
    previous_issue_keys: set[str] | None = None,
    repeated_issue_count: int = 1,
) -> RepairLoopDecision:
    editable, blocked = _partition_repair_issues(config, report.issues)
    if report.issues and not editable and blocked:
        return RepairLoopDecision(
            should_stop=True,
            reason="blocked_by_scope",
            editable_issue_ids=[],
            blocked_issue_ids=[issue.issue_id for issue in blocked],
        )
    if iteration >= config.max_iterations:
        return RepairLoopDecision(
            should_stop=True,
            reason="max_iterations",
            editable_issue_ids=[issue.issue_id for issue in editable],
            blocked_issue_ids=[issue.issue_id for issue in blocked],
        )
    if report.summary.errors <= config.stop_when.errors:
        if config.stop_when.allow_warnings or report.summary.warnings == 0:
            return RepairLoopDecision(
                should_stop=True,
                reason="warning_goal_met" if report.summary.warnings else "error_goal_met",
                editable_issue_ids=[issue.issue_id for issue in editable],
                blocked_issue_ids=[issue.issue_id for issue in blocked],
            )
    current_keys = {_issue_repeat_key(issue) for issue in editable}
    if (
        previous_issue_keys is not None
        and current_keys
        and current_keys == previous_issue_keys
        and repeated_issue_count >= config.stop_when.repeated_issue_limit
    ):
        return RepairLoopDecision(
            should_stop=True,
            reason="repeated_issue",
            editable_issue_ids=[issue.issue_id for issue in editable],
            blocked_issue_ids=[issue.issue_id for issue in blocked],
        )
    return RepairLoopDecision(
        should_stop=False,
        reason="continue",
        editable_issue_ids=[issue.issue_id for issue in editable],
        blocked_issue_ids=[issue.issue_id for issue in blocked],
    )


def repair_issue_is_editable(config: RepairLoopConfig, issue: ValidationIssue) -> bool:
    locked = set(config.repair_scope.locked_ids)
    editable = set(config.repair_scope.editable_ids)
    target = issue.repair_hint.target if issue.repair_hint is not None else None
    if target is not None and target in locked:
        return False
    if locked and issue.object_ids and all(object_id in locked for object_id in issue.object_ids):
        return False
    if not editable:
        return True
    if target is not None:
        return target in editable
    return any(object_id in editable for object_id in issue.object_ids)


def repair_issue_repeat_keys(report: ValidationReport, config: RepairLoopConfig | None = None) -> set[str]:
    issues = report.issues
    if config is not None:
        issues = [issue for issue in issues if repair_issue_is_editable(config, issue)]
    return {_issue_repeat_key(issue) for issue in issues}


def _partition_repair_issues(
    config: RepairLoopConfig,
    issues: list[ValidationIssue],
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    editable: list[ValidationIssue] = []
    blocked: list[ValidationIssue] = []
    for issue in issues:
        if repair_issue_is_editable(config, issue):
            editable.append(issue)
        else:
            blocked.append(issue)
    return editable, blocked


def _issue_repeat_key(issue: ValidationIssue) -> str:
    objects = ",".join(issue.object_ids)
    return f"{issue.type}:{objects}"
