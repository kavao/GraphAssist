"""ImageJob JSON の検証・実行・ログ。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from tools.graphassist.engine.executor import execute_job
from tools.graphassist.schema.job import ImageJob
from tools.graphassist.schema.paths import project_root


def load_job(json_path: Path) -> ImageJob:
    raw = json_path.read_text(encoding="utf-8")
    return ImageJob.model_validate_json(raw)


def replay_command(json_path: Path) -> list[str]:
    return [
        "uv",
        "run",
        "python",
        "tools/graphassist/graphassist.py",
        "job",
        str(json_path.as_posix()),
    ]


def write_logs(
    job: ImageJob,
    json_path: Path,
    steps: list[str],
    *,
    dry_run: bool,
    returncode: int = 0,
    stderr: str = "",
) -> Path:
    log_dir = project_root() / "generated" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = json_path.stem

    jsonl_path = log_dir / f"{ts}_{stem}.jsonl"
    md_path = log_dir / f"{ts}_{stem}.md"
    sh_path = log_dir / f"{ts}_{stem}_replay.sh"

    cmd = replay_command(json_path)
    record = {
        "timestamp": ts,
        "job_file": str(json_path),
        "job": job.model_dump(),
        "steps": steps,
        "dry_run": dry_run,
        "replay": cmd,
        "returncode": returncode,
        "stderr": stderr,
    }
    jsonl_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

    mode = "DRY RUN" if dry_run else "EXECUTE"
    md_path.write_text(
        f"# Image Job Log ({mode})\n\n"
        f"## Job file\n`{json_path}`\n\n"
        f"## Input\n`{job.input}`\n\n"
        f"## Output\n`{job.output}`\n\n"
        "## Steps\n"
        + "\n".join(f"- {s}" for s in steps)
        + "\n\n## Replay\n```bash\n"
        + " ".join(cmd)
        + "\n```\n",
        encoding="utf-8",
    )
    sh_path.write_text("#!/usr/bin/env bash\n" + " ".join(cmd) + "\n", encoding="utf-8")
    return jsonl_path


def run_job_file(json_path: Path, *, dry_run: bool = False) -> Path:
    root = project_root()
    job = load_job(json_path)
    output_path, steps = execute_job(job, root=root, dry_run=dry_run)
    write_logs(job, json_path, steps, dry_run=dry_run)
    if dry_run:
        print("DRY RUN:")
        for step in steps:
            print(f"  {step}")
        print(f"  -> {output_path}")
        return output_path

    print(f"created: {output_path}")
    return output_path
