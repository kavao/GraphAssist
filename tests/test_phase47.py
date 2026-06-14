"""Phase 4–7 機能のテスト。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tests.font_helper import ensure_test_font, test_font_rel
from graphassist.engine.executor import execute_job
from graphassist.engine.canvas import load
from graphassist.schema.job import ImageJob
from graphassist.schema.paths import project_root
from graphassist.util_cmd import (
    TrimOptions,
    run_contact_sheet,
    run_diff,
    run_inspect,
    run_palette,
    run_sheet_pack,
    run_sheet_split,
    run_trim,
)


class Phase47Test(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        ensure_test_font(self.root)
        self.src = self.root / "samples/source/phase47_base.png"
        self.src2 = self.root / "samples/source/phase47_cell.png"
        self.out = self.root / "generated/images/phase47_out.png"
        self.src.parent.mkdir(parents=True, exist_ok=True)
        (self.root / "generated/images").mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (80, 60), (0, 0, 0, 0)).save(self.src)
        img2 = Image.new("RGBA", (80, 60), (0, 0, 0, 0))
        px = img2.load()
        assert px is not None
        for y in range(20, 40):
            for x in range(30, 50):
                px[x, y] = (255, 0, 0, 255)
        img2.save(self.src2)
        Image.new("RGBA", (32, 32), (0, 255, 0, 255)).save(self.root / "samples/source/phase47_green.png")
        for path in (self.out,):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        for name in (
            "phase47_base.png",
            "phase47_cell.png",
            "phase47_green.png",
            "phase47_out.png",
            "phase47_trim.png",
            "phase47_diff.png",
            "phase47_sheet.png",
        ):
            for base in (self.root / "samples/source", self.root / "generated/images"):
                p = base / name
                if p.exists():
                    p.unlink()
        test_font = self.root / test_font_rel()
        if test_font.exists():
            test_font.unlink()
        split_dir = self.root / "generated/images/phase47_split"
        if split_dir.exists():
            for p in split_dir.glob("*.png"):
                p.unlink()
            split_dir.rmdir()

    def test_text_job(self) -> None:
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/phase47_base.png",
                "output": "generated/images/phase47_out.png",
                "operations": [
                    {
                        "type": "text",
                        "content": "GA",
                        "font": test_font_rel(),
                        "size": 24,
                        "color": "#ffffff",
                        "x": 10,
                        "y": 10,
                        "stroke_color": "black",
                        "stroke_width": 2,
                    }
                ],
            }
        )
        execute_job(job, root=self.root, dry_run=False)
        self.assertTrue(self.out.exists())

    def test_vertical_text_job(self) -> None:
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/phase47_base.png",
                "output": "generated/images/phase47_vertical_text.png",
                "operations": [
                    {
                        "type": "text",
                        "content": "AB",
                        "font": test_font_rel(),
                        "size": 16,
                        "color": "#ffffff",
                        "x": 10,
                        "y": 8,
                        "direction": "vertical",
                    }
                ],
            }
        )
        execute_job(job, root=self.root, dry_run=False)
        out = self.root / "generated/images/phase47_vertical_text.png"
        self.assertTrue(out.exists())

    def test_trim_and_flatten(self) -> None:
        out = self.root / "generated/images/phase47_trim.png"
        created = run_trim(self.src2, out, TrimOptions(background="transparent", padding=2))
        self.assertEqual(len(created), 1)
        trimmed = load(created[0])
        self.assertLess(trimmed.width, 80)
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/phase47_base.png",
                "output": "generated/images/phase47_out.png",
                "operations": [{"type": "flatten", "background": "white"}],
            }
        )
        execute_job(job, root=self.root, dry_run=False)

    def test_diff_inspect_palette(self) -> None:
        diff_out = self.root / "generated/images/phase47_diff.png"
        _, meta = run_diff(self.src, self.src2, diff_out)
        self.assertGreater(meta["changed_pixels"], 0)
        text = run_inspect(self.src2, fmt="json")
        data = json.loads(text)
        self.assertTrue(data["ok"])
        pal = json.loads(run_palette(self.src2, max_colors=4))
        self.assertGreater(len(pal["colors"]), 0)

    def test_sheet_commands(self) -> None:
        sheet = self.root / "generated/images/phase47_sheet.png"
        run_sheet_pack(
            self.root / "samples/source",
            sheet,
            cell_width=32,
            cell_height=32,
            cols=2,
            padding=0,
        )
        self.assertTrue(sheet.exists())
        split_dir = self.root / "generated/images/phase47_split"
        paths = run_sheet_split(sheet, split_dir, cell_width=32, cell_height=32, cols=2, rows=1, padding=0)
        self.assertGreaterEqual(len(paths), 1)
        contact = self.root / "generated/images/phase47_contact.png"
        run_contact_sheet(self.root / "samples/source", contact, cols=2, thumb=32, padding=2)
        self.assertTrue(contact.exists())


if __name__ == "__main__":
    unittest.main()
