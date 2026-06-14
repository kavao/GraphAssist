"""プロジェクトルートと安全パス。"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

INPUT_ROOT = "samples/source"
OUTPUT_ROOT = "generated"
FONT_ROOT = "assets/fonts"
RUNTIME_DIR = "runtime"
RUNTIME_FONT_ROOT = "runtime/assets/fonts"
MOSAIC_JSON_ROOTS = ("samples/mosaic", "generated/mosaic")
MOSAIC_OUTPUT_ROOT = "generated/mosaic"
JOB_ROOT = "samples/jobs"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def runtime_root(*, root: Path | None = None) -> Path:
    base = root or project_root()
    env = os.environ.get("GRAPHASSIST_RUNTIME")
    if env:
        return Path(env).resolve()
    return (base / RUNTIME_DIR).resolve()


def _under(base: Path, root_name: str) -> Path:
    return (base / root_name).resolve()


def resolve_input(path_str: str, *, root: Path | None = None, must_exist: bool = False) -> Path:
    base = root or project_root()
    resolved = _resolve_relative(path_str, base)
    safe = _under(base, INPUT_ROOT)
    if not str(resolved).startswith(str(safe)):
        raise ValueError(f"input must be under {INPUT_ROOT}/: {path_str}")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(resolved)
    return resolved


def resolve_output(path_str: str, *, root: Path | None = None) -> Path:
    base = root or project_root()
    resolved = _resolve_relative(path_str, base)
    safe = _under(base, OUTPUT_ROOT)
    if not str(resolved).startswith(str(safe)):
        raise ValueError(f"output must be under {OUTPUT_ROOT}/: {path_str}")
    return resolved


def resolve_mosaic_json(path_str: str, *, root: Path | None = None, must_exist: bool = False) -> Path:
    base = root or project_root()
    resolved = _resolve_relative(path_str, base)
    safe_roots = [_under(base, name) for name in MOSAIC_JSON_ROOTS]
    if not any(str(resolved).startswith(str(safe)) for safe in safe_roots):
        allowed = ", ".join(f"{name}/" for name in MOSAIC_JSON_ROOTS)
        raise ValueError(f"mosaic JSON must be under {allowed}: {path_str}")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(resolved)
    return resolved


def resolve_mosaic_output(path_str: str, *, root: Path | None = None) -> Path:
    base = root or project_root()
    resolved = _resolve_relative(path_str, base)
    safe = _under(base, MOSAIC_OUTPUT_ROOT)
    if not str(resolved).startswith(str(safe)):
        raise ValueError(f"mosaic output must be under {MOSAIC_OUTPUT_ROOT}/: {path_str}")
    return resolved


def resolve_batch_file(path_str: str, *, root: Path | None = None, must_exist: bool = False) -> Path:
    base = root or project_root()
    resolved = _resolve_relative(path_str, base)
    safe = _under(base, JOB_ROOT)
    if not str(resolved).startswith(str(safe)):
        raise ValueError(f"batch manifest must be under {JOB_ROOT}/: {path_str}")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(resolved)
    return resolved


def resolve_font(path_str: str, *, root: Path | None = None, must_exist: bool = False) -> Path:
    base = root or project_root()
    resolved = _resolve_relative(path_str, base)
    legacy = _under(base, FONT_ROOT)
    if not str(resolved).startswith(str(legacy)):
        raise ValueError(f"font must be under {FONT_ROOT}/: {path_str}")

    rel_name = Path(path_str).name
    candidates = [
        runtime_root(root=base) / "assets/fonts" / rel_name,
        resolved,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    if must_exist:
        raise FileNotFoundError(f"font not found: {path_str}")
    return resolved


def _resolve_relative(path_str: str, base: Path) -> Path:
    raw = Path(path_str)
    if raw.is_absolute():
        raise ValueError(f"absolute paths are not allowed: {path_str}")
    if ".." in raw.parts:
        raise ValueError(f"parent traversal is not allowed: {path_str}")
    return (base / raw).resolve()
