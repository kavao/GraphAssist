"""LineArt schema and SVG render tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from graphassist.engine.lineart.smooth import catmull_rom_to_commands
from graphassist.engine.lineart.svg_export import export_svg
from graphassist.graphassist import main
from graphassist.lineart_cmd import run_lineart_render
from graphassist.schema.lineart import LineArtDocument, PathCommand
from graphassist.schema.paths import project_root, resolve_lineart_input, resolve_lineart_output


class LineArtTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.sample = self.root / "samples/lineart/icon_minimal.json"
        self.output = self.root / "generated/vector/icon_minimal_test.svg"
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.unlink(missing_ok=True)

    def tearDown(self) -> None:
        self.output.unlink(missing_ok=True)

    def test_schema_accepts_metadata(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        document = LineArtDocument.model_validate(data)
        wave = document.layers[0].shapes[1]
        self.assertEqual(wave.role, "annotation")
        self.assertEqual(wave.container_id, "panel_01")
        self.assertFalse(wave.allow_overlap)
        self.assertEqual(wave.validation.severity, "warning")

    def test_schema_rejects_duplicate_ids(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        data["layers"][0]["shapes"][1]["id"] = "panel_01"
        with self.assertRaises(ValueError):
            LineArtDocument.model_validate(data)

    def test_path_command_value_count(self) -> None:
        self.assertEqual(PathCommand.from_raw(["L", 1, 2]).values, [1.0, 2.0])
        with self.assertRaises(ValueError):
            PathCommand.from_raw(["C", 1, 2])

    def test_catmull_rom_to_commands(self) -> None:
        commands = catmull_rom_to_commands([[0, 0], [10, 10], [20, 0]])
        self.assertEqual(commands[0].command, "M")
        self.assertEqual([command.command for command in commands[1:]], ["C", "C"])

    def test_export_svg(self) -> None:
        document = LineArtDocument.model_validate(json.loads(self.sample.read_text(encoding="utf-8")))
        svg = export_svg(document)
        self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', svg)
        self.assertIn('id="panel_01"', svg)
        self.assertIn('id="wave_01"', svg)
        self.assertIn('stroke-linecap="round"', svg)
        self.assertIn("C ", svg)

    def test_lineart_paths_are_restricted(self) -> None:
        self.assertTrue(resolve_lineart_input("samples/lineart/icon_minimal.json", root=self.root).exists())
        self.assertEqual(
            resolve_lineart_output("generated/vector/out.svg", root=self.root).name,
            "out.svg",
        )
        with self.assertRaises(ValueError):
            resolve_lineart_input("samples/source/not_lineart.json", root=self.root)
        with self.assertRaises(ValueError):
            resolve_lineart_output("generated/images/out.svg", root=self.root)

    def test_run_lineart_render_dry_run(self) -> None:
        out = run_lineart_render(
            Path("samples/lineart/icon_minimal.json"),
            Path("generated/vector/icon_minimal_test.svg"),
            root=self.root,
            dry_run=True,
        )
        self.assertEqual(out, self.output)
        self.assertFalse(self.output.exists())

    def test_run_lineart_render(self) -> None:
        out = run_lineart_render(
            Path("samples/lineart/icon_minimal.json"),
            Path("generated/vector/icon_minimal_test.svg"),
            root=self.root,
        )
        self.assertEqual(out, self.output)
        self.assertTrue(self.output.exists())
        self.assertIn("wave_01", self.output.read_text(encoding="utf-8"))

    def test_cli_lineart_render(self) -> None:
        code = main(
            [
                "lineart",
                "render",
                "samples/lineart/icon_minimal.json",
                "generated/vector/icon_minimal_test.svg",
            ]
        )
        self.assertEqual(code, 0)
        self.assertTrue(self.output.exists())


if __name__ == "__main__":
    unittest.main()
