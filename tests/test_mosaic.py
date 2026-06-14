"""MosaicArt（CharGrid）のテスト。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from graphassist.engine.mosaic_decode import render_mosaic
from graphassist.engine.mosaic_encode import encode_image, parse_grid
from graphassist.engine.mosaic_export import export_js
from graphassist.mosaic_cmd import MosaicDecodeOptions, MosaicEncodeOptions, run_decode, run_encode, run_export
from graphassist.schema.mosaic import MosaicArt
from graphassist.schema.paths import project_root


class MosaicTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.sample = self.root / "samples/mosaic/finale_rocket.json"
        self.out_png = self.root / "generated/images/mosaic_test_out.png"
        self.out_json = self.root / "generated/mosaic/mosaic_test_out.json"
        self.src_png = self.root / "samples/source/mosaic_test_src.png"
        (self.root / "generated/images").mkdir(parents=True, exist_ok=True)
        (self.root / "generated/mosaic").mkdir(parents=True, exist_ok=True)
        self.src_png.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (20, 20), (255, 95, 77, 255)).save(self.src_png)
        for path in (self.out_png, self.out_json):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        for path in (self.out_png, self.out_json, self.src_png):
            if path.exists():
                path.unlink()

    def test_parse_grid(self) -> None:
        self.assertEqual(parse_grid("10x8"), (10, 8))
        with self.assertRaises(ValueError):
            parse_grid("bad")

    def test_decode_finale_rocket(self) -> None:
        art = MosaicArt.model_validate(json.loads(self.sample.read_text(encoding="utf-8")))
        img = render_mosaic(art, cell_size=8)
        self.assertEqual(img.size, (64, 80))
        self.assertEqual(img.getpixel((0, 0))[3], 0)
        self.assertEqual(img.getpixel((24, 0))[:3], (215, 198, 235))

    def test_schema_rejects_bad_row(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        data["rows"][0] = data["rows"][0] + "X"
        with self.assertRaises(ValueError):
            MosaicArt.model_validate(data)

    def test_run_decode_cli(self) -> None:
        run_decode(
            self.sample,
            self.out_png,
            MosaicDecodeOptions(cell_size=4),
            root=self.root,
        )
        self.assertTrue(self.out_png.exists())
        self.assertEqual(Image.open(self.out_png).size, (32, 40))

    def test_export_js(self) -> None:
        art = MosaicArt.model_validate(json.loads(self.sample.read_text(encoding="utf-8")))
        text = export_js(art, name="FINALE_ROCKET")
        self.assertIn("const FINALE_ROCKET = [", text)
        self.assertIn("0xd7c6eb", text)
        self.assertIn("'...BB...'", text)

    def test_encode_and_roundtrip(self) -> None:
        run_encode(
            self.src_png,
            self.out_json,
            MosaicEncodeOptions(grid="4x4", max_colors=4),
            root=self.root,
        )
        art = MosaicArt.model_validate(json.loads(self.out_json.read_text(encoding="utf-8")))
        self.assertEqual(art.width, 4)
        self.assertEqual(art.height, 4)
        self.assertLessEqual(len(art.palette), 4)
        img = render_mosaic(art, cell_size=1)
        self.assertEqual(img.size, (4, 4))

    def test_run_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.js"
            # export to generated/mosaic via relative path
            rel_out = self.root / "generated/mosaic/mosaic_export_test.js"
            if rel_out.exists():
                rel_out.unlink()
            run_export(self.sample, fmt="js", output_path=rel_out, name="FINALE_ROCKET", root=self.root)
            self.assertTrue(rel_out.exists())
            rel_out.unlink()

    def test_encode_rgba_image(self) -> None:
        from graphassist.engine.mosaic_encode import encode_rgba_image

        img = Image.new("RGBA", (20, 20), (255, 95, 77, 255))
        art = encode_rgba_image(img, grid_width=4, grid_height=4, max_colors=4)
        self.assertEqual(art.width, 4)
        self.assertEqual(art.height, 4)
        self.assertLessEqual(len(art.palette), 4)

    def test_to_mosaic_op_schema(self) -> None:
        from graphassist.schema.ops import ToMosaicOp

        op = ToMosaicOp.model_validate(
            {
                "type": "to_mosaic",
                "grid": [16, 16],
                "mosaic_output": "generated/mosaic/out.json",
            }
        )
        self.assertEqual(op.grid, "16x16")

    def test_to_mosaic_must_be_last(self) -> None:
        from graphassist.schema.job import ImageJob

        with self.assertRaises(ValueError):
            ImageJob.model_validate(
                {
                    "version": "1.0",
                    "input": "samples/source/mosaic_test_src.png",
                    "output": "generated/images/out.png",
                    "operations": [
                        {"type": "to_mosaic", "grid": "8x8", "mosaic_output": "generated/mosaic/x.json"},
                        {"type": "resize", "long_edge": 32},
                    ],
                }
            )

    def test_to_mosaic_job(self) -> None:
        from graphassist.engine.executor import execute_job
        from graphassist.schema.job import ImageJob

        out_png = self.root / "generated/images/to_mosaic_preview.png"
        out_json = self.root / "generated/mosaic/to_mosaic_job.json"
        for path in (out_png, out_json):
            if path.exists():
                path.unlink()
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/mosaic_test_src.png",
                "output": "generated/images/to_mosaic_preview.png",
                "operations": [
                    {"type": "resize", "long_edge": 64},
                    {
                        "type": "to_mosaic",
                        "grid": "8x8",
                        "max_colors": 8,
                        "mosaic_output": "generated/mosaic/to_mosaic_job.json",
                    },
                ],
            }
        )
        execute_job(job, root=self.root, dry_run=False)
        self.assertTrue(out_png.exists())
        self.assertTrue(out_json.exists())
        art = MosaicArt.model_validate(json.loads(out_json.read_text(encoding="utf-8")))
        self.assertEqual(art.width, 8)
        self.assertEqual(art.height, 8)
        out_png.unlink(missing_ok=True)
        out_json.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
