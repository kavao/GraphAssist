"""Git 同梱フォント（最小セット）の定義。"""

from __future__ import annotations

from pathlib import Path

BUNDLED_FONT_NAMES: frozenset[str] = frozenset(
    {
        "DejaVuSans.ttf",
        "PixelMplus12-Regular.ttf",
    }
)


def bundled_font_path(root: Path, filename: str) -> Path | None:
    if filename not in BUNDLED_FONT_NAMES:
        return None
    path = root / "assets/fonts" / filename
    return path if path.is_file() else None


def list_bundled_fonts(root: Path) -> list[Path]:
    return [
        path
        for name in sorted(BUNDLED_FONT_NAMES)
        if (path := root / "assets/fonts" / name).is_file()
    ]
