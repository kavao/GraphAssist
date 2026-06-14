"""テスト用フォント配置。"""

from __future__ import annotations

import shutil
from pathlib import Path

FONT_REL = "assets/fonts/TestFont.ttf"

CANDIDATES = [
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/meiryo.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]


def ensure_test_font(root: Path) -> Path:
    dst = root / FONT_REL
    if dst.exists():
        return dst
    for candidate in CANDIDATES:
        if candidate.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(candidate, dst)
            return dst
    raise FileNotFoundError("no system font found for tests; place a TTF under assets/fonts/TestFont.ttf")


def test_font_rel() -> str:
    return FONT_REL
