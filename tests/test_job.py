"""ImageJob パイプラインのテスト。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from graphassist.engine.executor import execute_job
from graphassist.engine.canvas import load
from graphassist.schema.job import ImageJob
from graphassist.schema.paths import project_root


class JobTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.src = self.root / "samples/source/job_test_base.png"
        self.badge = self.root / "samples/source/job_test_badge.png"
        self.out = self.root / "generated/images/job_test_out.png"
        self.src.parent.mkdir(parents=True, exist_ok=True)
        (self.root / "generated/images").mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (100, 80), (200, 50, 50, 255)).save(self.src)
        Image.new("RGBA", (20, 20), (50, 100, 200, 128)).save(self.badge)
        if self.out.exists():
            self.out.unlink()

    def tearDown(self) -> None:
        for p in (self.src, self.badge, self.out):
            if p.exists():
                p.unlink()

    def test_resize_border_job(self) -> None:
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/job_test_base.png",
                "output": "generated/images/job_test_out.png",
                "operations": [
                    {"type": "resize", "width": 50, "height": 40},
                    {"type": "border", "size": 10, "color": "white"},
                ],
            }
        )
        execute_job(job, root=self.root, dry_run=False)
        img = load(self.out)
        self.assertEqual(img.size, (70, 60))

    def test_composite_job(self) -> None:
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/job_test_base.png",
                "output": "generated/images/job_test_out.png",
                "operations": [
                    {"type": "composite", "overlay": "samples/source/job_test_badge.png", "x": 5, "y": 5},
                ],
            }
        )
        execute_job(job, root=self.root, dry_run=False)
        self.assertTrue(self.out.exists())

    def test_center_crop(self) -> None:
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/job_test_base.png",
                "output": "generated/images/job_test_crop.png",
                "operations": [{"type": "crop", "width": 50, "height": 40, "anchor": "center"}],
            }
        )
        execute_job(job, root=self.root, dry_run=False)
        out = self.root / "generated/images/job_test_crop.png"
        self.assertTrue(out.exists())
        self.assertEqual(load(out).size, (50, 40))

    def test_dry_run(self) -> None:
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/job_test_base.png",
                "output": "generated/images/job_test_out.png",
                "operations": [{"type": "rotate", "degrees": 90}],
            }
        )
        _, steps = execute_job(job, root=self.root, dry_run=True)
        self.assertFalse(self.out.exists())
        self.assertIn("rotate", steps[1])

    def test_dry_run_input_asset_no_side_effects(self) -> None:
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input_asset": "ui-panel-dark",
                "output": "generated/images/job_test_out.png",
                "operations": [],
            }
        )
        with patch("graphassist.assets_cmd.materialize_catalog") as mock_mat:
            _, steps = execute_job(job, root=self.root, dry_run=True)
            mock_mat.assert_not_called()
        self.assertFalse(self.out.exists())
        self.assertIn("asset:ui-panel-dark", steps[0])

    def test_rejects_unsafe_output(self) -> None:
        with self.assertRaises(Exception):
            ImageJob.model_validate(
                {
                    "version": "1.0",
                    "input": "samples/source/job_test_base.png",
                    "output": "samples/source/evil.png",
                    "operations": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
