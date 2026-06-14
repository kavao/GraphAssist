"""色名・hex の解決。"""

from __future__ import annotations

import re

HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{6})$")

ALLOWED_COLOR_NAMES = frozenset(
    {"transparent", "white", "black", "red", "green", "blue", "gray"}
)


def parse_color(value: str) -> tuple[int, int, int, int]:
    if value.startswith("#"):
        match = HEX_COLOR_RE.match(value)
        if not match:
            raise ValueError(f"invalid hex color: {value}")
        body = match.group(1)
        return (
            int(body[0:2], 16),
            int(body[2:4], 16),
            int(body[4:6], 16),
            255,
        )
    return color_to_rgba(value)


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


def is_allowed_color(value: str) -> bool:
    if value.startswith("#"):
        return HEX_COLOR_RE.match(value) is not None
    return value.lower() in ALLOWED_COLOR_NAMES
