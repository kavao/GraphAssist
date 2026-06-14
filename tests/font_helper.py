"""テスト用フォント配置。"""

from __future__ import annotations

import shutil
from pathlib import Path

from graphassist.bundled_fonts import BUNDLED_FONT_NAMES, bundled_font_path

FONT_REL = "assets/fonts/TestFont.ttf"

CANDIDATES = [
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/meiryo.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]


def ensure_test_font(root: Path) -> Path:
    dst = root / FONT_REL
    if dst.exists():
        return dst
    bundled = bundled_font_path(root, "DejaVuSans.ttf")
    if bundled is not None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled, dst)
        return dst
    for candidate in CANDIDATES:
        if candidate.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(candidate, dst)
            return dst
    raise FileNotFoundError(
        "no font for tests; add assets/fonts/DejaVuSans.ttf (bundled) or a system TTF"
    )


def ensure_job_font(
    root: Path,
    rel_path: str,
    *,
    bootstrapped: list[Path] | None = None,
) -> Path:
    """Job 参照パスにフォントを用意する。Git 同梱があれば優先、なければテスト用フォントで代替。"""
    dest = root / rel_path
    if dest.is_file():
        return dest
    bundled = bundled_font_path(root, dest.name)
    if bundled is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled, dest)
        if bootstrapped is not None:
            bootstrapped.append(dest)
        return dest
    src = ensure_test_font(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    if bootstrapped is not None:
        bootstrapped.append(dest)
    return dest


def test_font_rel() -> str:
    return FONT_REL


def bundled_font_names() -> frozenset[str]:
    return BUNDLED_FONT_NAMES
