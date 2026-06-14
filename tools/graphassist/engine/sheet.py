"""スプライトシート・コンタクトシート。"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image

from tools.graphassist.engine.canvas import load, save


def contact_sheet(
    inputs: list[Path],
    output: Path,
    *,
    cols: int | None = None,
    thumb_width: int = 128,
    thumb_height: int | None = None,
    padding: int = 4,
    background: tuple[int, int, int, int] = (32, 32, 32, 255),
) -> Path:
    if not inputs:
        raise ValueError("no input images")
    thumbs: list[Image.Image] = []
    cell_h = thumb_height or thumb_width
    for path in inputs:
        img = load(path)
        thumbs.append(img.copy())
        thumbs[-1].thumbnail((thumb_width, cell_h), Image.Resampling.LANCZOS)

    count = len(thumbs)
    grid_cols = cols or max(1, math.ceil(math.sqrt(count)))
    grid_rows = math.ceil(count / grid_cols)
    sheet_w = grid_cols * thumb_width + (grid_cols + 1) * padding
    sheet_h = grid_rows * cell_h + (grid_rows + 1) * padding
    sheet = Image.new("RGBA", (sheet_w, sheet_h), background)

    for index, thumb in enumerate(thumbs):
        col = index % grid_cols
        row = index // grid_cols
        x = padding + col * (thumb_width + padding)
        y = padding + row * (cell_h + padding)
        sheet.paste(thumb, (x, y), thumb if thumb.mode == "RGBA" else None)

    save(sheet, output)
    return output


def sheet_pack(
    inputs: list[Path],
    output: Path,
    *,
    cell_width: int,
    cell_height: int,
    cols: int,
    padding: int = 0,
) -> Path:
    if not inputs:
        raise ValueError("no input images")
    rows = math.ceil(len(inputs) / cols)
    sheet_w = cols * cell_width + (cols - 1) * padding
    sheet_h = rows * cell_height + (rows - 1) * padding
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    for index, path in enumerate(inputs):
        img = load(path).convert("RGBA")
        img = img.resize((cell_width, cell_height), Image.Resampling.LANCZOS)
        col = index % cols
        row = index // cols
        x = col * (cell_width + padding)
        y = row * (cell_height + padding)
        sheet.paste(img, (x, y), img)

    save(sheet, output)
    return output


def sheet_split(
    input_path: Path,
    output_dir: Path,
    *,
    cell_width: int,
    cell_height: int,
    cols: int,
    rows: int,
    padding: int = 0,
    numbered: bool = True,
) -> list[Path]:
    img = load(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    index = 0
    for row in range(rows):
        for col in range(cols):
            x = col * (cell_width + padding)
            y = row * (cell_height + padding)
            if x + cell_width > img.width or y + cell_height > img.height:
                continue
            cell = img.crop((x, y, x + cell_width, y + cell_height))
            name = f"{index + 1:04d}.png" if numbered else f"cell_{row}_{col}.png"
            out = output_dir / name
            save(cell, out)
            created.append(out)
            index += 1
    if not created:
        raise ValueError("no cells extracted; check grid and image size")
    return created
