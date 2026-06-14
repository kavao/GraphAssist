"""GraphAssist convert tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from graphassist.convert_cmd import ConvertOptions, run_convert
from graphassist.engine.canvas import load


class ConvertTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        src = self.base / "in.png"
        Image.new("RGBA", (200, 100), (255, 0, 0, 128)).save(src)
        self.src = src
        self.out_dir = self.base / "out"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_long_edge_webp(self) -> None:
        opts = ConvertOptions(fmt="webp", long_edge=50)
        created = run_convert(self.src, self.out_dir / "a.webp", opts)
        self.assertEqual(len(created), 1)
        img = load(created[0])
        self.assertEqual(max(img.size), 50)

    def test_square_transparent_png(self) -> None:
        opts = ConvertOptions(fmt="png", square=True, square_fill="transparent")
        created = run_convert(self.src, self.out_dir / "sq.png", opts)
        img = load(created[0])
        self.assertEqual(img.size, (200, 200))
        corner = img.getpixel((0, 0))
        self.assertEqual(corner[3], 0)

    def test_batch_numbered(self) -> None:
        second = self.base / "in2.png"
        Image.new("RGB", (80, 80), (0, 255, 0)).save(second)
        indir = self.base / "batch_in"
        indir.mkdir()
        self.src.rename(indir / "a.png")
        second.rename(indir / "b.png")
        opts = ConvertOptions(fmt="png", numbered=True)
        created = run_convert(indir, self.out_dir, opts)
        self.assertEqual(len(created), 2)
        names = sorted(p.name for p in created)
        self.assertEqual(names, ["0001.png", "0002.png"])


if __name__ == "__main__":
    unittest.main()
