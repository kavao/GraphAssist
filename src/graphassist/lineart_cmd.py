"""LineArt CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

from graphassist.engine.lineart.svg_export import write_svg
from graphassist.schema.lineart import LineArtDocument
from graphassist.schema.paths import resolve_lineart_input, resolve_lineart_output


def load_lineart_document(path: Path) -> LineArtDocument:
    return LineArtDocument.model_validate(json.loads(path.read_text(encoding="utf-8")))


def run_lineart_render(
    json_path: Path,
    output: Path,
    *,
    root: Path | None = None,
    dry_run: bool = False,
) -> Path:
    input_path = resolve_lineart_input(str(json_path), root=root, must_exist=True)
    output_path = resolve_lineart_output(str(output), root=root)
    document = load_lineart_document(input_path)
    if dry_run:
        return output_path
    return write_svg(document, output_path)
