"""Font path resolution tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from graphassist.bundled_fonts import BUNDLED_FONT_NAMES, list_bundled_fonts
from graphassist.schema.paths import project_root, resolve_font


class FontPathTest(unittest.TestCase):
    def test_resolve_font_prefers_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime/assets/fonts"
            legacy = base / "assets/fonts"
            runtime.mkdir(parents=True)
            legacy.mkdir(parents=True)
            (runtime / "Demo.ttf").write_bytes(b"runtime")
            (legacy / "Demo.ttf").write_bytes(b"legacy")

            import os

            old = os.environ.get("GRAPHASSIST_RUNTIME")
            os.environ["GRAPHASSIST_RUNTIME"] = str(base / "runtime")
            try:
                path = resolve_font("assets/fonts/Demo.ttf", root=base, must_exist=True)
                self.assertEqual(path.read_bytes(), b"runtime")
            finally:
                if old is None:
                    os.environ.pop("GRAPHASSIST_RUNTIME", None)
                else:
                    os.environ["GRAPHASSIST_RUNTIME"] = old

    def test_git_bundled_fonts_present(self) -> None:
        root = project_root()
        bundled = list_bundled_fonts(root)
        self.assertEqual({p.name for p in bundled}, set(BUNDLED_FONT_NAMES))
        for path in bundled:
            self.assertGreater(path.stat().st_size, 10_000)

    def test_resolve_bundled_font_without_runtime(self) -> None:
        root = project_root()
        path = resolve_font(
            "assets/fonts/PixelMplus12-Regular.ttf",
            root=root,
            must_exist=True,
        )
        self.assertEqual(path.name, "PixelMplus12-Regular.ttf")
        self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
