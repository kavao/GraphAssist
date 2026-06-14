"""Batch manifest のテスト。"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.graphassist.batch_runner import load_manifest, run_batch_file  # noqa: E402
from tools.graphassist.schema.batch import BatchManifest  # noqa: E402
from tools.graphassist.schema.paths import project_root  # noqa: E402


class BatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.batch = self.root / "samples/jobs/mosaic_pipeline.json"
        self.out_file = self.root / "generated/images/finale_batch_file.png"
        self.out_inline = self.root / "generated/images/finale_batch_inline.png"
        self.out_js = self.root / "generated/mosaic/finale_rocket.js"
        for path in (self.out_file, self.out_inline, self.out_js):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        for path in (self.out_file, self.out_inline, self.out_js):
            if path.exists():
                path.unlink()

    def test_load_manifest(self) -> None:
        manifest = load_manifest(self.batch)
        self.assertIsInstance(manifest, BatchManifest)
        self.assertEqual(len(manifest.commands), 3)

    def test_validate_inline_decode_requires_one_source(self) -> None:
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "mosaic.decode",
                    "output": "generated/images/x.png",
                }
            ],
        }
        with self.assertRaises(ValueError):
            BatchManifest.model_validate(data)

    def test_run_batch(self) -> None:
        run_batch_file(self.batch, dry_run=False)
        self.assertTrue(self.out_file.exists())
        self.assertEqual(Image.open(self.out_file).size, (64, 80))
        self.assertTrue(self.out_inline.exists())
        self.assertEqual(Image.open(self.out_inline).size, (16, 8))
        self.assertTrue(self.out_js.exists())
        self.assertIn("FINALE_ROCKET", self.out_js.read_text(encoding="utf-8"))

    def test_dry_run(self) -> None:
        results = run_batch_file(self.batch, dry_run=True)
        self.assertEqual(len(results), 3)
        self.assertFalse(self.out_file.exists())


if __name__ == "__main__":
    unittest.main()
