"""Batch manifest の検証・順次実行。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from graphassist.analyze_cmd import run_analyze
from graphassist.assets_cmd import materialize_catalog
from graphassist.engine.executor import execute_job
from graphassist.lineart_cmd import run_lineart_render, run_lineart_validate
from graphassist.mosaic_cmd import (
    MosaicDecodeOptions,
    MosaicEncodeOptions,
    load_mosaic_json,
    run_decode_art,
    run_encode,
    run_export,
)
from graphassist.schema.batch import (
    AnalyzeCommand,
    AssetsMaterializeCommand,
    BatchManifest,
    JobCommand,
    LineArtRenderCommand,
    LineArtValidateCommand,
    MosaicDecodeCommand,
    MosaicEncodeCommand,
    MosaicExportCommand,
    command_output_path,
    is_batch_manifest,
)
from graphassist.schema.job import ImageJob
from graphassist.schema.paths import (
    normalize_manifest_path,
    project_root,
    resolve_batch_file,
    resolve_batch_image_input,
    resolve_output,
)


def load_manifest(json_path: Path) -> BatchManifest | ImageJob:
    raw = json.loads(json_path.read_text(encoding="utf-8"))
    if is_batch_manifest(raw):
        return BatchManifest.model_validate(raw)
    return ImageJob.model_validate(raw)


def run_batch_file(json_path: Path, *, dry_run: bool = False) -> list[str]:
    root = project_root()
    rel = str(json_path.relative_to(root)).replace("\\", "/") if json_path.is_absolute() else str(json_path).replace("\\", "/")
    resolved = resolve_batch_file(rel, root=root, must_exist=True)
    manifest = load_manifest(resolved)
    if isinstance(manifest, ImageJob):
        raise ValueError("file is a single ImageJob; use 'graphassist job' instead")

    results: list[str] = []
    steps: list[str] = []
    prev_output: str | None = None

    for index, command in enumerate(manifest.commands, start=1):
        label = f"[{index}/{len(manifest.commands)}] {command.type}"
        if dry_run:
            steps.append(f"{label} (dry-run)")
            results.append(_describe_command(command))
            prev_output = command_output_path(command)
            continue

        result = _execute_command(command, root=root, prev_output=prev_output)
        steps.append(f"{label} -> {result}")
        results.append(result)
        prev_output = command_output_path(command)

    _write_batch_log(resolved, manifest, steps, dry_run=dry_run)

    if dry_run:
        print("DRY RUN:")
        for step in steps:
            print(f"  {step}")
        for result in results:
            print(f"  -> {result}")
        return results

    for result in results:
        print(result)
    return results


def _is_chained_job_input(job_input: str | None, prev_output: str | None) -> bool:
    if job_input is None or prev_output is None:
        return False
    return normalize_manifest_path(job_input) == normalize_manifest_path(prev_output)


def _execute_command(command, *, root: Path, prev_output: str | None = None) -> str:
    if isinstance(command, JobCommand):
        chained = _is_chained_job_input(command.input, prev_output)
        execute_job(
            command.to_image_job(batch_chained=chained),
            root=root,
            dry_run=False,
            chained_input=chained,
        )
        return command.output

    if isinstance(command, MosaicDecodeCommand):
        opts = MosaicDecodeOptions(
            cell_size=command.cell_size,
            fmt=command.format,
            quality=command.quality,
        )
        if command.art is not None:
            out = run_decode_art(command.art, Path(command.output), opts, root=root)
        else:
            assert command.input is not None
            art = load_mosaic_json(Path(command.input), root=root)
            out = run_decode_art(art, Path(command.output), opts, root=root)
        return str(out)

    if isinstance(command, MosaicEncodeCommand):
        out = run_encode(
            Path(command.input),
            Path(command.output),
            MosaicEncodeOptions(
                grid=command.grid,
                max_colors=command.max_colors,
                transparent=command.transparent,
                alpha_threshold=command.alpha_threshold,
            ),
            root=root,
        )
        return str(out)

    if isinstance(command, MosaicExportCommand):
        assert command.input is not None
        out_path = Path(command.output) if command.output else None
        run_export(
            Path(command.input),
            fmt=command.format,
            output_path=out_path,
            name=command.name,
            root=root,
        )
        return command.output or f"stdout ({command.format})"

    if isinstance(command, LineArtRenderCommand):
        run_lineart_render(
            Path(command.input),
            Path(command.output),
            root=root,
            dry_run=False,
            png_output=Path(command.png_output) if command.png_output else None,
            png_width=command.png_width,
            validate_report=Path(command.validate_report) if command.validate_report else None,
        )
        return command.png_output or command.output

    if isinstance(command, LineArtValidateCommand):
        run_lineart_validate(
            Path(command.input),
            report=Path(command.report),
            root=root,
            dry_run=False,
        )
        return command.report

    if isinstance(command, AssetsMaterializeCommand):
        installed, missing = materialize_catalog(force=command.force, ids=command.ids)
        if missing:
            raise RuntimeError(f"assets.materialize failed: {', '.join(missing)}")
        return f"materialized: {', '.join(installed)}"

    if isinstance(command, AnalyzeCommand):
        input_path = resolve_batch_image_input(command.input, root=root, must_exist=True)
        compare_path = (
            resolve_batch_image_input(command.compare, root=root, must_exist=True)
            if command.compare
            else None
        )
        output_path = resolve_output(command.output, root=root)
        roi_specs = command.rois or []
        run_analyze(
            input_path,
            compare=compare_path,
            fmt="json",
            output=output_path,
            max_long_edge=command.max_long_edge,
            max_colors=command.max_colors,
            alpha_threshold=command.alpha_threshold,
            threshold_brightness=command.threshold_brightness,
            threshold_palette=command.threshold_palette,
            full_profiles=command.full_profiles,
            spatial=command.spatial,
            background=command.background,
            tolerance=command.tolerance,
            grid_rows=command.grid_rows,
            grid_cols=command.grid_cols,
            rois=[
                f"{r.name},{r.x},{r.y},{r.width},{r.height}"
                for r in roi_specs
            ]
            if roi_specs
            else None,
            root=root,
        )
        return str(command.output)

    raise TypeError(f"unsupported command: {type(command)}")


def _describe_command(command) -> str:
    if isinstance(command, JobCommand):
        return command.output
    if isinstance(command, MosaicDecodeCommand):
        return command.output
    if isinstance(command, MosaicEncodeCommand):
        return command.output
    if isinstance(command, MosaicExportCommand):
        return command.output or "stdout"
    if isinstance(command, LineArtRenderCommand):
        return command.png_output or command.output
    if isinstance(command, LineArtValidateCommand):
        return command.report
    if isinstance(command, AssetsMaterializeCommand):
        if command.ids:
            return f"materialized: {', '.join(command.ids)}"
        return "materialized: (all enabled catalog assets)"
    if isinstance(command, AnalyzeCommand):
        return command.output
    return "?"


def _write_batch_log(
    json_path: Path,
    manifest: BatchManifest,
    steps: list[str],
    *,
    dry_run: bool,
) -> Path:
    log_dir = project_root() / "generated" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = json_path.stem
    jsonl_path = log_dir / f"{ts}_{stem}_batch.jsonl"
    record = {
        "timestamp": ts,
        "batch_file": str(json_path),
        "command_count": len(manifest.commands),
        "steps": steps,
        "dry_run": dry_run,
        "replay": [
            "uv",
            "run",
            "graphassist",
            "run",
            str(json_path.as_posix()),
        ],
    }
    jsonl_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    return jsonl_path
