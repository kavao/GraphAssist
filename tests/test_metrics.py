"""Phase A + L metrics tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from graphassist.analyze_cmd import run_analyze
from graphassist.engine.metrics import MetricsOptions, analyze_image, compare_images
from graphassist.schema.paths import project_root


class MetricsTest(unittest.TestCase):
    def _save(self, path: Path, color: tuple[int, int, int, int], size: tuple[int, int] = (64, 64)) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", size, color).save(path)

    def test_white_black_compare_brightness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            white = root / "white.png"
            black = root / "black.png"
            self._save(white, (255, 255, 255, 255))
            self._save(black, (0, 0, 0, 255))
            result = compare_images(white, black, opts=MetricsOptions(max_long_edge=0))
            self.assertTrue(result["ok"])
            self.assertTrue(result["verdict"]["brightness_significantly_different"])
            self.assertEqual(result["verdict"]["brightness_relation"], "b_darker_than_a")

    def test_same_image_almost_same(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "same.png"
            self._save(path, (128, 128, 128, 255))
            result = compare_images(path, path, opts=MetricsOptions(max_long_edge=0))
            self.assertTrue(result["pixel"]["almost_same"])
            self.assertTrue(result["verdict"]["overall_similar"])

    def test_profile_luminance_white(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "white.png"
            self._save(path, (255, 255, 255, 255))
            profile = analyze_image(path, opts=MetricsOptions(max_long_edge=0))
            self.assertTrue(profile["ok"])
            self.assertGreater(profile["luminance"]["mean"], 0.95)

    def test_spatial_content_bbox_with_margin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "margins.png"
            img = Image.new("RGBA", (100, 80), (0, 0, 0, 0))
            for x in range(20, 80):
                for y in range(10, 60):
                    img.putpixel((x, y), (200, 100, 50, 255))
            img.save(path)
            profile = analyze_image(path, opts=MetricsOptions(max_long_edge=0, spatial=True))
            spatial = profile["spatial"]
            bbox = spatial["content_bbox"]
            self.assertEqual(bbox["x"], 20)
            self.assertEqual(bbox["y"], 10)
            self.assertEqual(bbox["width"], 60)
            self.assertEqual(bbox["height"], 50)
            self.assertEqual(spatial["edge_inset"]["left"], 20)
            self.assertTrue(spatial["verdict"]["has_transparent_margins"])

    def test_spatial_grid_brightest_center(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "grid.png"
            img = Image.new("RGBA", (90, 90), (0, 0, 0, 0))
            for x in range(30, 60):
                for y in range(30, 60):
                    img.putpixel((x, y), (255, 255, 255, 255))
            img.save(path)
            profile = analyze_image(
                path,
                opts=MetricsOptions(max_long_edge=0, spatial=True, grid_rows=3, grid_cols=3),
            )
            self.assertEqual(profile["spatial"]["verdict"]["brightest_tile"], "r1c1")

    def test_spatial_roi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roi.png"
            self._save(path, (255, 0, 0, 255), size=(40, 40))
            profile = analyze_image(
                path,
                opts=MetricsOptions(
                    max_long_edge=0,
                    spatial=True,
                    rois=[{"name": "corner", "x": 0, "y": 0, "width": 10, "height": 10}],
                ),
            )
            rois = profile["spatial"]["rois"]
            self.assertEqual(len(rois), 1)
            self.assertEqual(rois[0]["name"], "corner")
            self.assertGreater(rois[0]["luminance"]["mean"], 0.2)

    def test_analyze_cli_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.png"
            self._save(path, (128, 128, 128, 255))
            text = run_analyze(path, fmt="json", max_long_edge=0)
            data = json.loads(text)
            self.assertEqual(data["kind"], "profile")
            self.assertTrue(data["ok"])

    def test_batch_analyze_schema(self) -> None:
        from graphassist.schema.batch import AnalyzeCommand

        cmd = AnalyzeCommand.model_validate(
            {
                "type": "analyze",
                "input": "samples/source/job_test_base.png",
                "output": "generated/logs/test_analyze.json",
                "spatial": True,
            }
        )
        self.assertTrue(cmd.spatial)

    def test_adjust_op_schema(self) -> None:
        from graphassist.schema.ops import AdjustOp

        op = AdjustOp.model_validate({"type": "adjust", "brightness": 1.2})
        self.assertEqual(op.brightness, 1.2)

    def test_adjust_changes_luminance(self) -> None:
        from graphassist.engine.executor import execute_job
        from graphassist.schema.job import ImageJob

        root = project_root()
        src = root / "samples/source/metrics_adjust_in.png"
        out = root / "generated/images/metrics_adjust_out.png"
        src.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (32, 32), (80, 80, 80, 255)).save(src)
        if out.exists():
            out.unlink()
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/metrics_adjust_in.png",
                "output": "generated/images/metrics_adjust_out.png",
                "operations": [{"type": "adjust", "brightness": 2.0}],
            }
        )
        execute_job(job, root=root, dry_run=False)
        before = analyze_image(src, opts=MetricsOptions(max_long_edge=0))
        after = analyze_image(out, opts=MetricsOptions(max_long_edge=0))
        self.assertGreater(after["luminance"]["mean"], before["luminance"]["mean"])
        src.unlink(missing_ok=True)
        out.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
