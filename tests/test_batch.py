"""Batch manifest のテスト。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from PIL import Image

from graphassist.batch_runner import load_manifest, run_batch_file
from graphassist.schema.batch import BatchManifest
from graphassist.schema.paths import project_root


class BatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.batch = self.root / "samples/jobs/mosaic_pipeline.json"
        self.out_file = self.root / "generated/images/finale_batch_file.png"
        self.out_inline = self.root / "generated/images/finale_batch_inline.png"
        self.out_js = self.root / "generated/mosaic/finale_rocket.js"
        self.catalog_batch = self.root / "samples/jobs/demo_catalog_pipeline.json"
        self.out_catalog = self.root / "generated/images/demo_catalog_pipeline.png"
        for path in (self.out_file, self.out_inline, self.out_js, self.out_catalog):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        for path in (self.out_file, self.out_inline, self.out_js, self.out_catalog):
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

    def test_assets_materialize_command_schema(self) -> None:
        manifest = load_manifest(self.catalog_batch)
        self.assertIsInstance(manifest, BatchManifest)
        self.assertEqual(len(manifest.commands), 2)
        self.assertEqual(manifest.commands[0].type, "assets.materialize")

    def test_validate_unknown_catalog_id(self) -> None:
        data = {
            "version": "1.0",
            "commands": [{"type": "assets.materialize", "ids": ["not-a-real-catalog-id"]}],
        }
        with self.assertRaises(ValueError):
            BatchManifest.model_validate(data)

    def test_catalog_pipeline_dry_run(self) -> None:
        results = run_batch_file(self.catalog_batch, dry_run=True)
        self.assertEqual(len(results), 2)
        self.assertIn("materialized:", results[0])
        self.assertFalse(self.out_catalog.exists())

    def test_pipeline_asset_ids_schema(self) -> None:
        batch = self.root / "samples/jobs/demo_catalog_pipeline_asset_ids.json"
        manifest = load_manifest(batch)
        self.assertEqual(len(manifest.commands), 2)
        self.assertEqual(manifest.commands[0].type, "assets.materialize")
        self.assertEqual(manifest.commands[1].type, "job")

    def test_run_catalog_pipeline(self) -> None:
        run_batch_file(self.catalog_batch, dry_run=False)
        self.assertTrue(self.out_catalog.exists())
        self.assertGreater(self.out_catalog.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
