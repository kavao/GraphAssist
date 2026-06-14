"""プロジェクトルートと安全パス。"""

from __future__ import annotations

from pathlib import Path

INPUT_ROOT = "samples/source"
OUTPUT_ROOT = "generated"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


def _resolve_relative(path_str: str, base: Path) -> Path:
    raw = Path(path_str)
    if raw.is_absolute():
        raise ValueError(f"absolute paths are not allowed: {path_str}")
    if ".." in raw.parts:
        raise ValueError(f"parent traversal is not allowed: {path_str}")
    return (base / raw).resolve()
