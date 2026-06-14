"""テスト用フォント配置。"""

from __future__ import annotations

import shutil
from pathlib import Path

FONT_REL = "assets/fonts/TestFont.ttf"

BUNDLED_FONT = Path(__file__).resolve().parent / "fixtures" / "DejaVuSans.ttf"

CANDIDATES = [
    BUNDLED_FONT,
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
    for candidate in CANDIDATES:
        if candidate.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(candidate, dst)
            return dst
    raise FileNotFoundError(
        "no font for tests; add tests/fixtures/DejaVuSans.ttf or a system TTF"
    )


def test_font_rel() -> str:
    return FONT_REL
