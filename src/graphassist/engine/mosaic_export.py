"""MosaicArt JSON のエクスポート。"""

from __future__ import annotations

import json
import re

from graphassist.schema.mosaic import MosaicArt, parse_hex_color


def export_js(art: MosaicArt, *, name: str | None = None) -> str:
    const_name = _const_name(name or (art.meta.title if art.meta and art.meta.title else "MOSAIC_ART"))
    rows_lines = ",\n".join(f"  '{row}'" for row in art.rows)
    color_lines = ",\n".join(
        f"  {key}: 0x{parse_hex_color(value)[0]:02x}{parse_hex_color(value)[1]:02x}{parse_hex_color(value)[2]:02x}"
        for key, value in sorted(art.palette.items())
    )
    return (
        f"const {const_name} = [\n{rows_lines},\n];\n\n"
        f"const {const_name}_COLORS = {{\n{color_lines},\n}};\n"
    )


def export_json(art: MosaicArt) -> str:
    return json.dumps(art.model_dump(exclude_none=True), ensure_ascii=False, indent=2) + "\n"


def _const_name(raw: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z_]+", "_", raw).strip("_").upper()
    if not cleaned:
        return "MOSAIC_ART"
    if cleaned[0].isdigit():
        return f"MOSAIC_{cleaned}"
    return cleaned
