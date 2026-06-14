#!/usr/bin/env python3
"""Regenerate samples/source/demo_text_base.png for demo_zangyo_extend.json."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from graphassist.schema.paths import project_root, resolve_font

OUTPUT = Path("samples/source/demo_text_base.png")
WIDTH, HEIGHT = 400, 600


def _font(path: str, size: int, *, root: Path) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(resolve_font(path, root=root, must_exist=True)), size)


def build_demo_base(root: Path) -> Image.Image:
    font_jp = "assets/fonts/NotoSansJP-Regular.otf"
    font_en = "assets/fonts/InterVariable.ttf"

    img = Image.new("RGBA", (WIDTH, HEIGHT), (13, 21, 40, 255))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        t = y / HEIGHT
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(int(13 + t * 8), int(21 + t * 5), int(40 + t * 12), 255),
        )

    draw.rectangle([0, 0, WIDTH, 56], fill=(26, 26, 46, 255))
    draw.line([(0, 56), (WIDTH, 56)], fill=(240, 224, 64, 180), width=2)
    draw.text(
        (20, 14),
        "定時退社シミュレータ",
        font=_font(font_jp, 22, root=root),
        fill=(220, 225, 235, 255),
    )

    draw.rounded_rectangle(
        [16, 80, 200, 340], radius=8, fill=(30, 38, 58, 255), outline=(80, 90, 120, 255), width=1
    )
    menu_font = _font(font_jp, 16, root=root)
    y = 100
    for item in ("ホーム", "実績", "設定"):
        draw.rounded_rectangle([28, y, 188, y + 36], radius=4, fill=(40, 48, 72, 255))
        draw.text((40, y + 8), item, font=menu_font, fill=(180, 190, 210, 255))
        y += 52

    draw.rounded_rectangle(
        [16, 360, 280, 520], radius=8, fill=(22, 30, 50, 255), outline=(60, 70, 100, 255), width=1
    )
    body_font = _font(font_jp, 15, root=root)
    draw.text((28, 378), "本日の退社時刻", font=body_font, fill=(160, 170, 190, 255))
    draw.text((28, 408), "18:00", font=_font(font_en, 36, root=root), fill=(100, 220, 140, 255))
    draw.text((28, 468), "あと 30 分で定時です", font=body_font, fill=(140, 150, 170, 255))

    draw.rectangle([300, 72, 392, 580], fill=(18, 24, 42, 200))
    draw.line([(300, 72), (300, 580)], fill=(240, 224, 64, 80), width=1)
    draw.text((308, 80), "EVENT", font=_font(font_jp, 12, root=root), fill=(120, 130, 150, 255))

    draw.rectangle([0, HEIGHT - 40, WIDTH, HEIGHT], fill=(20, 20, 36, 255))
    draw.text(
        (20, HEIGHT - 28),
        "GraphAssist demo base",
        font=_font(font_en, 13, root=root),
        fill=(100, 110, 130, 255),
    )
    return img


def main() -> int:
    root = project_root()
    dest = root / OUTPUT
    try:
        img = build_demo_base(root)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print("Run scripts/setup-runtime.ps1 (or .sh) to fetch fonts first.", file=sys.stderr)
        return 1

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG")
    print(f"created: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
