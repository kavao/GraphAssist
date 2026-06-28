"""FontVector outline extraction tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from graphassist.font_cmd import run_font_outline
from graphassist.graphassist import main
from graphassist.schema.font_outline import FontOutlineDocument
from graphassist.schema.paths import project_root, resolve_font_outline_output


try:
    import fontTools  # noqa: F401

    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False


class FontOutlineSchemaTest(unittest.TestCase):
    def test_schema_round_trip_uses_raw_path_commands(self) -> None:
        document = FontOutlineDocument.model_validate(
            {
                "version": "1.0",
                "source_text": "G",
                "font": "assets/fonts/DejaVuSans.ttf",
                "font_size": 96,
                "layout": "horizontal",
                "metrics": {
                    "units_per_em": 2048,
                    "ascender": 89.0625,
                    "descender": -22.2656,
                    "width": 74.3906,
                    "height": 111.3281,
                },
                "glyphs": [
                    {
                        "char": "G",
                        "glyph_name": "G",
                        "origin": [0, 0],
                        "advance": 74.3906,
                        "commands": [["M", 1, 2], ["L", 3, 4], ["Z"]],
                    }
                ],
                "default_fill": {"type": "solid", "color": "#111111"},
                "default_stroke": None,
            }
        )
        payload = document.model_dump(mode="json")
        self.assertEqual(payload["glyphs"][0]["commands"][0], ["M", 1.0, 2.0])


@unittest.skipUnless(HAS_FONTTOOLS, "fonttools optional extra is not installed")
class FontOutlineExtractionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.output = self.root / "generated/vector/font_outline_test.json"
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.unlink(missing_ok=True)

    def tearDown(self) -> None:
        self.output.unlink(missing_ok=True)

    def test_extract_latin_glyph(self) -> None:
        out = run_font_outline(
            text="G",
            font=Path("assets/fonts/DejaVuSans.ttf"),
            size=96,
            output=Path("generated/vector/font_outline_test.json"),
            root=self.root,
            dry_run=False,
            strict=True,
        )
        self.assertEqual(out, self.output)
        document = FontOutlineDocument.model_validate(json.loads(self.output.read_text(encoding="utf-8")))
        self.assertEqual(document.source_text, "G")
        self.assertEqual(document.glyphs[0].char, "G")
        self.assertGreater(len(document.glyphs[0].commands), 4)
        self.assertEqual(document.glyphs[0].commands[0].command, "M")
        self.assertGreater(document.glyphs[0].advance, 0)

    def test_extract_string_layout_advances_origin(self) -> None:
        run_font_outline(
            text="GA",
            font=Path("assets/fonts/DejaVuSans.ttf"),
            size=64,
            output=Path("generated/vector/font_outline_test.json"),
            root=self.root,
            strict=True,
        )
        document = FontOutlineDocument.model_validate(json.loads(self.output.read_text(encoding="utf-8")))
        self.assertEqual([glyph.char for glyph in document.glyphs], ["G", "A"])
        self.assertGreater(document.glyphs[1].origin[0], document.glyphs[0].origin[0])
        self.assertAlmostEqual(document.glyphs[1].origin[0], document.glyphs[0].advance, places=3)

    def test_font_outline_paths_are_restricted(self) -> None:
        self.assertEqual(
            resolve_font_outline_output("generated/vector/out.font-outline.json", root=self.root).name,
            "out.font-outline.json",
        )
        with self.assertRaises(ValueError):
            resolve_font_outline_output("generated/images/out.font-outline.json", root=self.root)

    def test_run_font_outline_dry_run(self) -> None:
        out = run_font_outline(
            text="G",
            font=Path("assets/fonts/DejaVuSans.ttf"),
            size=96,
            output=Path("generated/vector/font_outline_test.json"),
            root=self.root,
            dry_run=True,
            strict=True,
        )
        self.assertEqual(out, self.output)
        self.assertFalse(self.output.exists())

    def test_cli_font_outline(self) -> None:
        code = main(
            [
                "font",
                "outline",
                "--text",
                "G",
                "--font",
                "assets/fonts/DejaVuSans.ttf",
                "--size",
                "96",
                "--output",
                "generated/vector/font_outline_test.json",
                "--strict",
            ]
        )
        self.assertEqual(code, 0)
        self.assertTrue(self.output.exists())


if __name__ == "__main__":
    unittest.main()
