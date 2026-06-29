"""FontVector CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

from graphassist.engine.font.extract import extract_font_outline
from graphassist.engine.font.lineart_convert import font_outline_to_lineart, lineart_document_to_json_payload
from graphassist.schema.font_outline import FontOutlineDocument
from graphassist.schema.lineart import LineArtDocument
from graphassist.schema.paths import resolve_font, resolve_font_outline_output, resolve_lineart_json_output


def run_font_outline(
    *,
    text: str,
    font: Path,
    size: float,
    output: Path,
    root: Path | None = None,
    dry_run: bool = False,
    strict: bool = False,
    lineart_output: Path | None = None,
) -> Path:
    font_ref = str(font).replace("\\", "/")
    font_path = resolve_font(font_ref, root=root, must_exist=True)
    output_path = resolve_font_outline_output(str(output), root=root)
    lineart_output_path = (
        resolve_lineart_json_output(str(lineart_output), root=root)
        if lineart_output is not None
        else None
    )
    document = extract_font_outline(
        text=text,
        font_path=font_path,
        font_ref=font_ref,
        font_size=size,
        strict=strict,
    )
    if dry_run:
        return output_path
    write_font_outline(document, output_path)
    if lineart_output_path is not None:
        write_font_lineart(font_outline_to_lineart(document), lineart_output_path)
    return output_path


def write_font_outline(document: FontOutlineDocument, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = document.model_dump(mode="json")
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_font_lineart(document: LineArtDocument, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(lineart_document_to_json_payload(document), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
