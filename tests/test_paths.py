"""Font path resolution tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from graphassist.schema.paths import resolve_font


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


if __name__ == "__main__":
    unittest.main()
