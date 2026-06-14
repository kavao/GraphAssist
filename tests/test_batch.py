"""Batch manifest のテスト。"""

from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from PIL import Image

from graphassist.batch_runner import load_manifest, run_batch_file
from graphassist.schema.batch import BatchManifest
from graphassist.schema.paths import project_root
from tests.font_helper import ensure_test_font


class BatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.batch = self.root / "samples/jobs/mosaic_pipeline.json"
        self.out_file = self.root / "generated/images/finale_batch_file.png"
        self.out_inline = self.root / "generated/images/finale_batch_inline.png"
        self.out_js = self.root / "generated/mosaic/finale_rocket.js"
        self.catalog_batch = self.root / "samples/jobs/demo_catalog_pipeline.json"
        self.out_catalog = self.root / "generated/images/demo_catalog_pipeline.png"
        self.birds_batch = self.root / "samples/jobs/birds_on_trunk_pipeline.json"
        self.out_birds_base = self.root / "generated/images/birds_on_trunk_base.png"
        self.out_birds = self.root / "generated/images/birds_on_trunk.png"
        self._bootstrapped_fonts: list[Path] = []
        for path in (
            self.out_file,
            self.out_inline,
            self.out_js,
            self.out_catalog,
            self.out_birds_base,
            self.out_birds,
        ):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        for path in (
            self.out_file,
            self.out_inline,
            self.out_js,
            self.out_catalog,
            self.out_birds_base,
            self.out_birds,
        ):
            if path.exists():
                path.unlink()
        for font_path in self._bootstrapped_fonts:
            if font_path.exists():
                font_path.unlink()

    def _ensure_font(self, rel_path: str) -> None:
        """CI には runtime/fonts が無いため、参照フォントをバンドル済みテストフォントで bootstrap する。"""
        font_path = self.root / rel_path
        if font_path.exists():
            return
        src = ensure_test_font(self.root)
        font_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, font_path)
        self._bootstrapped_fonts.append(font_path)

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
        self._ensure_font("assets/fonts/NotoSansJP-Regular.otf")
        run_batch_file(self.catalog_batch, dry_run=False)
        self.assertTrue(self.out_catalog.exists())
        self.assertGreater(self.out_catalog.stat().st_size, 0)

    def test_birds_pipeline_schema(self) -> None:
        manifest = load_manifest(self.birds_batch)
        self.assertIsInstance(manifest, BatchManifest)
        self.assertEqual(len(manifest.commands), 2)
        self.assertEqual(manifest.commands[0].type, "mosaic.decode")
        self.assertEqual(manifest.commands[1].type, "job")

    def test_validate_generated_job_input_without_chain(self) -> None:
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "job",
                    "input": "generated/images/orphan.png",
                    "output": "generated/images/out.png",
                    "operations": [{"type": "resize", "long_edge": 64}],
                }
            ],
        }
        with self.assertRaises(ValueError):
            BatchManifest.model_validate(data)

    def test_validate_generated_job_input_mismatch(self) -> None:
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "mosaic.decode",
                    "input": "samples/mosaic/finale_rocket.json",
                    "output": "generated/images/step1.png",
                    "cell_size": 8,
                },
                {
                    "type": "job",
                    "input": "generated/images/wrong.png",
                    "output": "generated/images/out.png",
                    "operations": [{"type": "resize", "long_edge": 64}],
                },
            ],
        }
        with self.assertRaises(ValueError):
            BatchManifest.model_validate(data)

    def test_run_birds_pipeline(self) -> None:
        self._ensure_font("assets/fonts/PixelMplus12-Regular.ttf")
        run_batch_file(self.birds_batch, dry_run=False)
        self.assertTrue(self.out_birds_base.exists())
        self.assertTrue(self.out_birds.exists())
        self.assertEqual(Image.open(self.out_birds_base).size, (400, 208))
        self.assertEqual(Image.open(self.out_birds).size, (400, 264))


if __name__ == "__main__":
    unittest.main()
