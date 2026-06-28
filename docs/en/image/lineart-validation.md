# LineArt Validation Report / Repair Loop

English · [日本語](../../ja/image/lineart-validation.md)

This page defines the first format for saving LineArt geometry validation results as JSON and feeding that report back into an LLM repair loop. Validation Report JSON v0.1 describes what is broken; Repair Loop v0.1 describes what may be changed and how many repair attempts are allowed.

## When To Use This Document

Use this after generating LineArt JSON when you want to mechanically check overlap, overflow, connector mistakes, or unintended intersections.

The minimal prompt can be:

```text
Validate this LineArt JSON and create a repair-loop report.
```

With that prompt, the assistant prepares a validation flow and stores issues as Validation Report JSON. After implementation, `lineart validate --report` should emit this format.

## Overall Flow

```text
LineArt JSON
  ↓
Geometry validation
  ↓
Validation Report JSON v0.1
  ↓
Repair Loop v0.1
  ↓
LLM repairs the JSON
  ↓
Revalidate
```

## Validation Report JSON v0.1

The report stores validation results in a form both humans and LLMs can read. It avoids free-form feedback alone and includes target objects, positions, metrics, and repair hints.

```json
{
  "version": "0.1",
  "validation_result": "failed",
  "source": {
    "document_id": "flow_01",
    "input_path": "samples/lineart/flow_01.json"
  },
  "summary": {
    "errors": 1,
    "warnings": 1,
    "info": 0
  },
  "issues": [
    {
      "issue_id": "LV-0001",
      "type": "connector_misaligned",
      "severity": "error",
      "object_ids": ["arrow_01", "node_a", "node_b"],
      "position": [320, 180],
      "metric": {
        "distance_to_target": 18.5,
        "max_allowed_distance": 4
      },
      "message": "arrow_01 does not touch node_b.",
      "repair_hint": {
        "action": "move_endpoint",
        "target": "arrow_01",
        "anchor": "to",
        "toward": "node_b"
      }
    }
  ]
}
```

## Report Fields

| Field | Purpose |
|-------|---------|
| `version` | Report format version. The initial value is `"0.1"`. |
| `validation_result` | One of `passed`, `failed`, or `warning_only`. |
| `source` | Identity of the validated LineArt JSON. |
| `summary` | Counts of errors, warnings, and info items. |
| `issues[]` | List of detected issues. |

## Issue Fields

| Field | Purpose |
|-------|---------|
| `issue_id` | Unique ID within the report. |
| `type` | Issue type, such as `overlap`, `outside_container`, or `connector_misaligned`. |
| `severity` | One of `error`, `warning`, or `info`. |
| `object_ids` | Shape ids involved in the issue. |
| `position` | Representative issue position. Optional. |
| `metric` | Numeric details such as distance, area, and thresholds. |
| `message` | Short human-readable explanation. |
| `repair_hint` | Structured hint for the LLM repair step. |

## Initial repair_hint Fields

| Field | Purpose |
|-------|---------|
| `action` | Repair type, such as `move`, `move_endpoint`, `resize`, `reroute`, `reorder_layer`, or `keep_clear`. |
| `target` | Shape id to repair. |
| `anchor` | Sub-target such as connector `from` or `to`. |
| `toward` | Shape id the target should move toward. |
| `delta` | Movement such as `[dx, dy]`. |
| `constraints` | Conditions to preserve while repairing. |

## Repair Loop v0.1

Repair Loop defines how an LLM should use a Validation Report to repair a LineArt document.

```json
{
  "version": "0.1",
  "mode": "patch_preferred",
  "max_iterations": 3,
  "stop_when": {
    "errors": 0,
    "allow_warnings": true
  },
  "repair_scope": {
    "locked_ids": ["logo_mark"],
    "editable_ids": ["arrow_01", "label_01"]
  },
  "inputs": {
    "lineart_document": "current document JSON",
    "validation_report": "Validation Report JSON v0.1"
  }
}
```

## Repair Loop Policy

- Prefer targeted patches first; full regeneration is the last resort.
- Do not move shapes listed in `locked_ids`.
- Stop when `errors` reaches 0.
- Decide whether warnings are acceptable with `stop_when.allow_warnings`.
- Stop at the maximum iteration count when the same `issue_id` or `type` remains.

## Relationship To Metadata

LineArt Metadata stores what the drawing intends. Validation Report stores what actually failed. Repair Loop returns that difference to the LLM for correction.

```text
metadata: label_01 should be inside panel_01
validation: label_01 is outside panel_01
repair: move label_01 into panel_01
```

## Update Policy

This page should evolve alongside geometry validation. When adding a new issue type, first add a small value under `issues[].type` and `repair_hint.action`; promote it into the shared schema only after multiple validators need it.
