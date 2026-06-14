"""Mosaic merge / compose tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from graphassist.engine.mosaic_decode import render_mosaic
from graphassist.engine.mosaic_merge import MergeLayer, add_branch_trunk, compose_birds_on_trunk, merge_mosaics
from graphassist.mosaic_cmd import load_mosaic_json, run_compose_birds, run_merge
from graphassist.schema.mosaic import MosaicArt
from graphassist.schema.paths import project_root


class MosaicMergeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.merged_out = self.root / "generated/mosaic/test_merge_out.json"
        if self.merged_out.exists():
            self.merged_out.unlink()

    def tearDown(self) -> None:
        if self.merged_out.exists():
            self.merged_out.unlink()

    def test_merge_two_layers(self) -> None:
        left = MosaicArt.model_validate(
            {
                "version": "1.0",
                "width": 2,
                "height": 2,
                "transparent": ".",
                "palette": {"A": "#ff0000"},
                "rows": ["A.", ".A"],
            }
        )
        right = MosaicArt.model_validate(
            {
                "version": "1.0",
                "width": 2,
                "height": 2,
                "transparent": ".",
                "palette": {"B": "#00ff00"},
                "rows": ["BB", "BB"],
            }
        )
        merged = merge_mosaics(
            width=4,
            height=2,
            layers=[MergeLayer(left), MergeLayer(right, x=2, y=0)],
            title="merged",
        )
        self.assertEqual(merged.width, 4)
        self.assertEqual(merged.rows[0], "A.BB")
        self.assertEqual(len(merged.palette), 2)

    def test_add_branch_trunk_templates(self) -> None:
        trunk = add_branch_trunk(17, 10, trunk_top_row=5, row_templates=("...HHHHHHHHHHH...",))
        self.assertEqual(trunk.rows[5], "...HHHHHHHHHHH...")

    def test_compose_birds_visual_match(self) -> None:
        canonical = load_mosaic_json(self.root / "samples/mosaic/birds_on_trunk.json", root=self.root)
        merged = compose_birds_on_trunk(
            load_mosaic_json(self.root / "samples/mosaic/parakeet.json", root=self.root),
            load_mosaic_json(self.root / "samples/mosaic/parrot.json", root=self.root),
        )
        img_a = render_mosaic(canonical, cell_size=8)
        img_b = render_mosaic(merged, cell_size=8)
        self.assertEqual(img_a.size, (400, 208))
        px_a = img_a.load()
        px_b = img_b.load()
        assert px_a is not None and px_b is not None
        match = total = 0
        for y in range(img_a.height):
            for x in range(img_a.width):
                if px_a[x, y][3] > 0 or px_b[x, y][3] > 0:
                    total += 1
                    if px_a[x, y] == px_b[x, y]:
                        match += 1
        self.assertGreaterEqual(match / total, 0.85)

    def test_run_merge_cli(self) -> None:
        out = run_merge(
            self.merged_out,
            canvas="50x26",
            layers=[
                "samples/mosaic/parakeet.json@8,6",
                "samples/mosaic/parrot.json@24,3",
            ],
            title="cli_merge",
            root=self.root,
        )
        self.assertTrue(out.exists())
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["width"], 50)

    def test_run_compose_birds_cli(self) -> None:
        out = run_compose_birds(self.merged_out, root=self.root)
        self.assertTrue(out.exists())
        art = MosaicArt.model_validate(json.loads(out.read_text(encoding="utf-8")))
        self.assertEqual(art.meta.title if art.meta else None, "birds_on_trunk")


if __name__ == "__main__":
    unittest.main()
