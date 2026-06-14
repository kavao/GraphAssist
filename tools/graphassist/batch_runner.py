"""Batch manifest の検証・順次実行。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from tools.graphassist.engine.executor import execute_job
from tools.graphassist.mosaic_cmd import (
    MosaicDecodeOptions,
    MosaicEncodeOptions,
    load_mosaic_json,
    run_decode_art,
    run_encode,
    run_export,
)
from tools.graphassist.schema.batch import (
    BatchManifest,
    JobCommand,
    MosaicDecodeCommand,
    MosaicEncodeCommand,
    MosaicExportCommand,
    is_batch_manifest,
)
from tools.graphassist.schema.job import ImageJob
from tools.graphassist.schema.paths import project_root, resolve_batch_file


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

    for index, command in enumerate(manifest.commands, start=1):
        label = f"[{index}/{len(manifest.commands)}] {command.type}"
        if dry_run:
            steps.append(f"{label} (dry-run)")
            results.append(_describe_command(command))
            continue

        result = _execute_command(command, root=root)
        steps.append(f"{label} -> {result}")
        results.append(result)

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


def _execute_command(command, *, root: Path) -> str:
    if isinstance(command, JobCommand):
        execute_job(command.to_image_job(), root=root, dry_run=False)
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
            "python",
            "tools/graphassist/graphassist.py",
            "run",
            str(json_path.as_posix()),
        ],
    }
    jsonl_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    return jsonl_path
