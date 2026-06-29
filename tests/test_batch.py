"""Batch manifest のテスト。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from PIL import Image

from graphassist.batch_runner import load_manifest, run_batch_file
from graphassist.schema.batch import BatchManifest
from graphassist.schema.paths import project_root
from tests.font_helper import ensure_job_font


def _has_svg_raster_backend() -> bool:
    try:
        import resvg_py  # noqa: F401

        return True
    except ImportError:
        pass
    try:
        import cairosvg  # noqa: F401

        return True
    except ImportError:
        return False


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
        self.lineart_batch = self.root / "samples/jobs/lineart_icon_pipeline.json"
        self.lineart_repair_batch = self.root / "samples/jobs/lineart_repair_loop_validate.json"
        self.out_lineart_svg = self.root / "generated/vector/lineart_icon_pipeline.svg"
        self.out_lineart_base = self.root / "generated/images/lineart_icon_pipeline_base.png"
        self.out_lineart = self.root / "generated/images/lineart_icon_pipeline.png"
        self.out_lineart_report = self.root / "generated/logs/lineart_icon_pipeline_validation_test.json"
        self.out_lineart_repair_report = self.root / "generated/logs/lineart_repair_loop_validation.json"
        self._bootstrapped_fonts: list[Path] = []
        for path in (
            self.out_file,
            self.out_inline,
            self.out_js,
            self.out_catalog,
            self.out_birds_base,
            self.out_birds,
            self.out_lineart_svg,
            self.out_lineart_base,
            self.out_lineart,
            self.out_lineart_report,
            self.out_lineart_repair_report,
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
            self.out_lineart_svg,
            self.out_lineart_base,
            self.out_lineart,
            self.out_lineart_report,
            self.out_lineart_repair_report,
        ):
            if path.exists():
                path.unlink()
        for font_path in self._bootstrapped_fonts:
            if font_path.exists():
                font_path.unlink()

    def _ensure_font(self, rel_path: str) -> None:
        """Git 同梱またはテスト用フォントで Job 参照パスを用意する。"""
        ensure_job_font(self.root, rel_path, bootstrapped=self._bootstrapped_fonts)

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

    def test_lineart_pipeline_schema(self) -> None:
        manifest = load_manifest(self.lineart_batch)
        self.assertIsInstance(manifest, BatchManifest)
        self.assertEqual(len(manifest.commands), 2)
        self.assertEqual(manifest.commands[0].type, "lineart.render")
        self.assertEqual(manifest.commands[1].type, "job")

    def test_lineart_validate_command_schema(self) -> None:
        manifest = BatchManifest.model_validate(
            {
                "version": "1.0",
                "commands": [
                    {
                        "type": "lineart.validate",
                        "input": "samples/lineart/icon_minimal.json",
                        "report": "generated/logs/lineart_icon_pipeline_validation_test.json",
                    }
                ],
            }
        )
        self.assertEqual(manifest.commands[0].type, "lineart.validate")

    def test_lineart_repair_loop_validate_schema(self) -> None:
        manifest = load_manifest(self.lineart_repair_batch)
        self.assertIsInstance(manifest, BatchManifest)
        self.assertEqual(len(manifest.commands), 1)
        self.assertEqual(manifest.commands[0].type, "lineart.validate")

    def test_lineart_pipeline_dry_run(self) -> None:
        results = run_batch_file(self.lineart_batch, dry_run=True)
        self.assertEqual(
            results,
            [
                "generated/images/lineart_icon_pipeline_base.png",
                "generated/images/lineart_icon_pipeline.png",
            ],
        )
        self.assertFalse(self.out_lineart_base.exists())
        self.assertFalse(self.out_lineart.exists())

    def test_lineart_validate_command_dry_run(self) -> None:
        manifest_path = self.root / "samples/jobs/lineart_validate_test.json"
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "lineart.validate",
                    "input": "samples/lineart/icon_minimal.json",
                    "report": "generated/logs/lineart_icon_pipeline_validation_test.json",
                }
            ],
        }
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        try:
            results = run_batch_file(manifest_path, dry_run=True)
        finally:
            manifest_path.unlink(missing_ok=True)
        self.assertEqual(results, ["generated/logs/lineart_icon_pipeline_validation_test.json"])
        self.assertFalse(self.out_lineart_report.exists())

    def test_run_lineart_validate_command(self) -> None:
        manifest_path = self.root / "samples/jobs/lineart_validate_test.json"
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "lineart.validate",
                    "input": "samples/lineart/icon_minimal.json",
                    "report": "generated/logs/lineart_icon_pipeline_validation_test.json",
                }
            ],
        }
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        try:
            results = run_batch_file(manifest_path, dry_run=False)
        finally:
            manifest_path.unlink(missing_ok=True)
        self.assertEqual(results, ["generated/logs/lineart_icon_pipeline_validation_test.json"])
        self.assertTrue(self.out_lineart_report.exists())

    def test_run_lineart_repair_loop_validate_sample(self) -> None:
        results = run_batch_file(self.lineart_repair_batch, dry_run=False)
        self.assertEqual(results, ["generated/logs/lineart_repair_loop_validation.json"])
        self.assertTrue(self.out_lineart_repair_report.exists())
        data = json.loads(self.out_lineart_repair_report.read_text(encoding="utf-8"))
        self.assertEqual(data["validation_result"], "failed")
        self.assertGreaterEqual(data["summary"]["errors"], 2)

    @unittest.skipUnless(_has_svg_raster_backend(), "resvg-py or cairosvg is not installed")
    def test_run_lineart_pipeline(self) -> None:
        run_batch_file(self.lineart_batch, dry_run=False)
        self.assertTrue(self.out_lineart_svg.exists())
        self.assertTrue(self.out_lineart_base.exists())
        self.assertTrue(self.out_lineart.exists())
        with Image.open(self.out_lineart_base) as image:
            self.assertEqual(image.size[0], 128)
        with Image.open(self.out_lineart) as image:
            self.assertEqual(image.size, (148, 148))

    def test_validate_generated_job_input_after_lineart_mismatch(self) -> None:
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "lineart.render",
                    "input": "samples/lineart/icon_minimal.json",
                    "output": "generated/vector/step.svg",
                    "png_output": "generated/images/step.png",
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
        run_batch_file(self.birds_batch, dry_run=False)
        self.assertTrue(self.out_birds_base.exists())
        self.assertTrue(self.out_birds.exists())
        self.assertEqual(Image.open(self.out_birds_base).size, (400, 208))
        self.assertEqual(Image.open(self.out_birds).size, (400, 264))

    def test_validate_generated_analyze_input_without_chain(self) -> None:
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "analyze",
                    "input": "generated/images/orphan.png",
                    "output": "generated/logs/orphan.json",
                }
            ],
        }
        with self.assertRaises(ValueError):
            BatchManifest.model_validate(data)

    def test_validate_analyze_compare_not_in_prior(self) -> None:
        data = {
            "version": "1.0",
            "commands": [
                {
                    "type": "job",
                    "input": "samples/source/job_test_base.png",
                    "output": "generated/images/step_a.png",
                    "operations": [],
                },
                {
                    "type": "analyze",
                    "input": "generated/images/step_a.png",
                    "compare": "generated/images/missing.png",
                    "output": "generated/logs/bad_compare.json",
                },
            ],
        }
        with self.assertRaises(ValueError):
            BatchManifest.model_validate(data)

    def test_run_analyze_chain_after_job(self) -> None:
        src = self.root / "samples/source/job_test_base.png"
        before = self.root / "generated/images/tone_before.png"
        after = self.root / "generated/images/tone_after.png"
        log = self.root / "generated/logs/tone_compare.json"
        src.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (32, 32), (80, 80, 80, 255)).save(src)
        for path in (before, after, log):
            if path.exists():
                path.unlink()
        batch = self.root / "samples/jobs/tone_analyze_pipeline.json"
        run_batch_file(batch, dry_run=False)
        self.assertTrue(before.exists())
        self.assertTrue(after.exists())
        self.assertTrue(log.exists())
        payload = json.loads(log.read_text(encoding="utf-8"))
        self.assertEqual(payload["kind"], "compare")
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["verdict"]["brightness_significantly_different"])
        src.unlink(missing_ok=True)
        before.unlink(missing_ok=True)
        after.unlink(missing_ok=True)
        log.unlink(missing_ok=True)

    def test_dry_run_analyze_chain(self) -> None:
        batch = self.root / "samples/jobs/tone_analyze_pipeline.json"
        results = run_batch_file(batch, dry_run=True)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[-1], "generated/logs/tone_compare.json")


if __name__ == "__main__":
    unittest.main()
