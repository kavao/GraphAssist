"""Phase T2-T5 transform operation tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from graphassist.convert_cmd import ConvertOptions, apply_tone_transforms, run_convert
from graphassist.engine.executor import apply_operation, execute_job
from graphassist.engine.metrics import MetricsOptions, analyze_image
from graphassist.schema.job import ImageJob
from graphassist.schema.ops import (
    AdjustOp,
    BlurOp,
    CurveOp,
    PosterizeOp,
    QuantizeOp,
    SharpenOp,
)
from graphassist.schema.paths import project_root


class TransformTest(unittest.TestCase):
    def _rgba(self, color: tuple[int, int, int, int], size: tuple[int, int] = (32, 32)) -> Image.Image:
        return Image.new("RGBA", size, color)

    def test_curve_op_levels_validation(self) -> None:
        with self.assertRaises(ValueError):
            CurveOp.model_validate({"type": "curve", "mode": "levels", "black": 200, "white": 100})

    def test_quantize_op_bounds(self) -> None:
        with self.assertRaises(ValueError):
            QuantizeOp.model_validate({"type": "quantize", "colors": 1})

    def test_adjust_darkens_black(self) -> None:
        img = self._rgba((0, 0, 0, 255))
        out = apply_operation(img, AdjustOp(type="adjust", brightness=0.5), root=project_root())
        self.assertEqual(out.getpixel((0, 0)), (0, 0, 0, 255))

    def test_gamma_darkens_midtone(self) -> None:
        img = self._rgba((128, 128, 128, 255))
        out = apply_operation(img, CurveOp(type="curve", mode="gamma", gamma=2.0), root=project_root())
        r, g, b, a = out.getpixel((0, 0))
        self.assertEqual(a, 255)
        self.assertLess(r, 128)

    def test_levels_stretches_range(self) -> None:
        img = self._rgba((128, 128, 128, 255))
        out = apply_operation(
            img,
            CurveOp(type="curve", mode="levels", black=64, white=192),
            root=project_root(),
        )
        r, _, _, a = out.getpixel((0, 0))
        self.assertEqual(a, 255)
        self.assertAlmostEqual(r, 128, delta=2)

    def test_quantize_reduces_colors(self) -> None:
        img = Image.new("RGBA", (16, 16))
        pixels = img.load()
        assert pixels is not None
        for x in range(16):
            for y in range(16):
                pixels[x, y] = (x * 16, y * 16, 128, 255)
        out = apply_operation(img, QuantizeOp(type="quantize", colors=4, dither=False), root=project_root())
        colors = {out.getpixel((x, y)) for x in range(16) for y in range(16)}
        self.assertLessEqual(len(colors), 4)

    def test_posterize_reduces_levels(self) -> None:
        img = self._rgba((200, 100, 50, 255))
        out = apply_operation(img, PosterizeOp(type="posterize", bits=2), root=project_root())
        r, g, b, a = out.getpixel((0, 0))
        self.assertEqual(a, 255)
        self.assertEqual(r % 64, 0)

    def test_blur_zero_is_unchanged(self) -> None:
        img = self._rgba((10, 20, 30, 255))
        out = apply_operation(img, BlurOp(type="blur", radius=0), root=project_root())
        self.assertEqual(out.tobytes(), img.tobytes())

    def test_blur_preserves_alpha(self) -> None:
        img = self._rgba((255, 0, 0, 0))
        out = apply_operation(img, BlurOp(type="blur", radius=2.0), root=project_root())
        self.assertEqual(out.getpixel((0, 0))[3], 0)

    def test_sharpen_enhance_identity(self) -> None:
        img = self._rgba((40, 80, 120, 255))
        out = apply_operation(img, SharpenOp(type="sharpen", kind="enhance", amount=1.0), root=project_root())
        self.assertEqual(out.getpixel((0, 0)), (40, 80, 120, 255))

    def test_pipeline_adjust_then_blur(self) -> None:
        img = Image.new("RGBA", (24, 24), (100, 100, 100, 255))
        img = apply_operation(img, AdjustOp(type="adjust", brightness=1.5), root=project_root())
        out = apply_operation(img, BlurOp(type="blur", kind="gaussian", radius=1.0), root=project_root())
        self.assertEqual(out.mode, "RGBA")
        self.assertEqual(out.size, (24, 24))

    def test_rgba_alpha_unchanged_after_quantize(self) -> None:
        img = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        pixels = img.load()
        assert pixels is not None
        pixels[4, 4] = (255, 0, 0, 255)
        out = apply_operation(img, QuantizeOp(type="quantize", colors=2), root=project_root())
        self.assertEqual(out.getpixel((0, 0))[3], 0)
        self.assertEqual(out.getpixel((4, 4))[3], 255)

    def test_convert_tone_brightness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src.png"
            dst = root / "out.png"
            Image.new("RGBA", (16, 16), (80, 80, 80, 255)).save(src)
            before = analyze_image(src, opts=MetricsOptions(max_long_edge=0))
            img = Image.open(src)
            out_img = apply_tone_transforms(img, ConvertOptions(brightness=2.0))
            out_img.save(dst)
            after = analyze_image(dst, opts=MetricsOptions(max_long_edge=0))
            self.assertGreater(after["luminance"]["mean"], before["luminance"]["mean"])

    def test_convert_cli_with_gamma(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "in.png"
            out_dir = root / "out"
            Image.new("RGBA", (12, 12), (128, 128, 128, 255)).save(src)
            created = run_convert(src, out_dir, ConvertOptions(gamma=2.0))
            self.assertEqual(len(created), 1)
            arr = np.array(Image.open(created[0]).convert("RGB"))
            self.assertLess(arr[0, 0, 0], 128)

    def test_job_tone_chain_with_project_paths(self) -> None:
        root = project_root()
        src = root / "samples/source/transform_tone_in.png"
        out = root / "generated/images/transform_tone_out.png"
        src.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (24, 24), (60, 60, 60, 255)).save(src)
        if out.exists():
            out.unlink()
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/transform_tone_in.png",
                "output": "generated/images/transform_tone_out.png",
                "operations": [
                    {"type": "adjust", "brightness": 1.3},
                    {"type": "quantize", "colors": 8},
                ],
            }
        )
        execute_job(job, root=root, dry_run=False)
        self.assertTrue(out.exists())
        src.unlink(missing_ok=True)
        out.unlink(missing_ok=True)

    def test_grayscale_luminance(self) -> None:
        from graphassist.schema.ops import GrayscaleOp

        img = self._rgba((200, 100, 50, 255))
        out = apply_operation(img, GrayscaleOp(type="grayscale", mode="luminance"), root=project_root())
        r, g, b, a = out.getpixel((0, 0))
        self.assertEqual(a, 255)
        self.assertEqual(r, g)
        self.assertEqual(g, b)
        self.assertLess(r, 200)

    def test_sepia_strength_zero_unchanged(self) -> None:
        from graphassist.schema.ops import SepiaOp

        img = self._rgba((200, 100, 50, 255))
        out = apply_operation(img, SepiaOp(type="sepia", strength=0.0), root=project_root())
        self.assertEqual(out.getpixel((0, 0)), (200, 100, 50, 255))

    def test_sepia_tints_channels(self) -> None:
        from graphassist.schema.ops import SepiaOp

        img = self._rgba((0, 128, 255, 255))
        out = apply_operation(img, SepiaOp(type="sepia", strength=1.0), root=project_root())
        r, g, b, a = out.getpixel((0, 0))
        self.assertEqual(a, 255)
        self.assertNotEqual((r, g, b), (0, 128, 255))
        self.assertGreater(r, g)

    def test_grayscale_preserves_alpha(self) -> None:
        from graphassist.schema.ops import GrayscaleOp

        img = self._rgba((255, 0, 0, 0))
        out = apply_operation(img, GrayscaleOp(type="grayscale"), root=project_root())
        self.assertEqual(out.getpixel((0, 0))[3], 0)

    def test_convert_grayscale_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "in.png"
            out_dir = root / "out"
            Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(src)
            created = run_convert(src, out_dir, ConvertOptions(grayscale=True))
            pixel = Image.open(created[0]).getpixel((0, 0))
            self.assertEqual(pixel[0], pixel[1])
            self.assertEqual(pixel[1], pixel[2])


if __name__ == "__main__":
    unittest.main()
