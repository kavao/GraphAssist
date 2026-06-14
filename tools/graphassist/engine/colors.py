"""色名の解決。"""

from __future__ import annotations

ALLOWED_COLOR_NAMES = frozenset(
    {"transparent", "white", "black", "red", "green", "blue", "gray"}
)


def color_to_rgba(name: str) -> tuple[int, int, int, int]:
    key = name.lower()
    if key not in ALLOWED_COLOR_NAMES:
        raise ValueError(f"color is not allowed: {name}")
    table: dict[str, tuple[int, int, int, int]] = {
        "transparent": (0, 0, 0, 0),
        "white": (255, 255, 255, 255),
        "black": (0, 0, 0, 255),
        "red": (255, 0, 0, 255),
        "green": (0, 128, 0, 255),
        "blue": (0, 0, 255, 255),
        "gray": (128, 128, 128, 255),
    }
    return table[key]
