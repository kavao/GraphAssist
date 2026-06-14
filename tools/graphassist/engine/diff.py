"""差分画像生成。"""

from __future__ import annotations

import numpy as np
from PIL import Image


def diff_images(before: Image.Image, after: Image.Image, *, threshold: int = 16) -> tuple[Image.Image, dict]:
    a = np.array(before.convert("RGBA"), dtype=np.int16)
    b = np.array(after.convert("RGBA"), dtype=np.int16)
    if a.shape != b.shape:
        raise ValueError(f"image sizes differ: {before.size} vs {after.size}")

    delta = np.abs(a - b)
    changed = np.any(delta > threshold, axis=2)
    diff_count = int(changed.sum())
    total = changed.size
    ratio = diff_count / total if total else 0.0

    out = np.zeros_like(a, dtype=np.uint8)
    out[changed] = [255, 0, 0, 255]
    out[~changed] = [0, 0, 0, 0]

    meta = {
        "width": before.width,
        "height": before.height,
        "changed_pixels": diff_count,
        "total_pixels": total,
        "changed_ratio": round(ratio, 6),
        "almost_same": diff_count == 0,
    }
    return Image.fromarray(out, mode="RGBA"), meta
