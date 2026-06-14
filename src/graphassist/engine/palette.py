"""パレット抽出。"""

from __future__ import annotations

from collections import Counter

from PIL import Image


def extract_palette(img: Image.Image, *, max_colors: int = 16) -> list[dict]:
    if max_colors < 1 or max_colors > 256:
        raise ValueError("max_colors must be 1..256")
    rgba = img.convert("RGBA")
    opaque = [tuple(p) for p in rgba.getdata() if p[3] > 0]
    if not opaque:
        return []

    counts = Counter(opaque)
    if len(counts) <= max_colors:
        ranked: list[tuple[tuple[int, int, int, int], int]] = counts.most_common()
    else:
        sample = Image.new("RGB", (len(opaque), 1))
        px = sample.load()
        assert px is not None
        for i, (r, g, b, _a) in enumerate(opaque):
            px[i, 0] = (r, g, b)
        q = sample.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()
        if pal is None:
            raise RuntimeError("failed to quantize palette")
        index_counts = Counter(q.getdata())
        palette_rgbs = [
            (pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2], 255) for i in range(max_colors)
        ]
        ranked = [
            (palette_rgbs[idx], count)
            for idx, count in index_counts.most_common(max_colors)
            if idx < len(palette_rgbs)
        ]

    total = sum(count for _rgb, count in ranked)
    result: list[dict] = []
    for (r, g, b, a), count in ranked:
        result.append(
            {
                "hex": f"#{r:02x}{g:02x}{b:02x}",
                "rgba": [r, g, b, a],
                "count": count,
                "ratio": round(count / total, 4) if total else 0.0,
            }
        )
    return result
