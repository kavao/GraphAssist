"""LineArt schema and SVG render tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from PIL import Image

from graphassist.engine.lineart.smooth import catmull_rom_to_commands
from graphassist.engine.lineart.svg_export import export_svg
from graphassist.graphassist import main
from graphassist.lineart_cmd import run_lineart_render
from graphassist.schema.lineart import LineArtDocument, PathCommand
from graphassist.schema.paths import (
    project_root,
    resolve_lineart_input,
    resolve_lineart_output,
    resolve_lineart_raster_output,
)


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


class LineArtTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = project_root()
        self.sample = self.root / "samples/lineart/icon_minimal.json"
        self.output = self.root / "generated/vector/icon_minimal_test.svg"
        self.png_output = self.root / "generated/images/icon_minimal_test.png"
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.png_output.parent.mkdir(parents=True, exist_ok=True)
        self.output.unlink(missing_ok=True)
        self.png_output.unlink(missing_ok=True)

    def tearDown(self) -> None:
        self.output.unlink(missing_ok=True)
        self.png_output.unlink(missing_ok=True)

    def test_schema_accepts_metadata(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        document = LineArtDocument.model_validate(data)
        wave = next(shape for shape in document.layers[0].shapes if shape.id == "wave_01")
        self.assertEqual(wave.role, "annotation")
        self.assertEqual(wave.container_id, "panel_01")
        self.assertFalse(wave.allow_overlap)
        self.assertEqual(wave.validation.severity, "warning")

    def test_schema_rejects_duplicate_ids(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        data["layers"][0]["shapes"][1]["id"] = "panel_01"
        with self.assertRaises(ValueError):
            LineArtDocument.model_validate(data)

    def test_schema_accepts_primitives(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        document = LineArtDocument.model_validate(data)
        shape_types = {shape.id: shape.type for shape in document.layers[0].shapes}
        self.assertEqual(shape_types["panel_01"], "rect")
        self.assertEqual(shape_types["badge_01"], "star")
        self.assertEqual(shape_types["dot_01"], "ellipse")
        self.assertEqual(shape_types["triangle_01"], "polygon")

    def test_schema_accepts_gradients(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        document = LineArtDocument.model_validate(data)
        panel = next(shape for shape in document.layers[0].shapes if shape.id == "panel_01")
        self.assertEqual(document.definitions.gradients["panel_gradient"].type, "linear")
        self.assertEqual(panel.fill.type, "gradient")
        self.assertEqual(panel.fill.ref, "panel_gradient")

    def test_schema_accepts_group_transform_clip(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        document = LineArtDocument.model_validate(data)
        group = next(shape for shape in document.layers[0].shapes if shape.id == "group_01")
        self.assertEqual(group.type, "group")
        self.assertEqual(group.clip_path, "badge_clip")
        self.assertEqual(group.opacity, 0.85)
        self.assertEqual(group.transform.rotate, -8)
        self.assertEqual(len(group.shapes), 2)

    def test_schema_rejects_bad_clip_reference(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        group = next(shape for shape in data["layers"][0]["shapes"] if shape["id"] == "group_01")
        group["clip_path"] = "missing_clip"
        with self.assertRaises(ValueError):
            LineArtDocument.model_validate(data)

    def test_schema_rejects_duplicate_nested_id(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        group = next(shape for shape in data["layers"][0]["shapes"] if shape["id"] == "group_01")
        group["shapes"][0]["id"] = "panel_01"
        with self.assertRaises(ValueError):
            LineArtDocument.model_validate(data)

    def test_schema_rejects_bad_gradient_reference(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        panel = next(shape for shape in data["layers"][0]["shapes"] if shape["id"] == "panel_01")
        panel["fill"]["ref"] = "missing_gradient"
        with self.assertRaises(ValueError):
            LineArtDocument.model_validate(data)

    def test_schema_rejects_bad_gradient_stops(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        data["definitions"]["gradients"]["panel_gradient"]["stops"] = [
            {"offset": 1, "color": "#ffffff"},
            {"offset": 0, "color": "#dbeafe"},
        ]
        with self.assertRaises(ValueError):
            LineArtDocument.model_validate(data)

    def test_schema_rejects_bad_star_radius(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        star = next(shape for shape in data["layers"][0]["shapes"] if shape["id"] == "badge_01")
        star["inner_radius"] = star["outer_radius"]
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
        self.assertIn("<defs>", svg)
        self.assertIn('<linearGradient id="panel_gradient"', svg)
        self.assertIn('<clipPath id="badge_clip"', svg)
        self.assertIn('fill="url(#panel_gradient)"', svg)
        self.assertIn('id="panel_01"', svg)
        self.assertIn('id="group_01"', svg)
        self.assertIn('clip-path="url(#badge_clip)"', svg)
        self.assertIn('opacity="0.85"', svg)
        self.assertIn('transform="translate(0 0) rotate(-8 84 90) scale(1)"', svg)
        self.assertIn('id="wave_01"', svg)
        self.assertIn("<rect ", svg)
        self.assertIn("<ellipse ", svg)
        self.assertIn("<polygon ", svg)
        self.assertIn('id="badge_01"', svg)
        self.assertIn('stroke-linecap="round"', svg)
        self.assertIn('fill="none"', svg)
        self.assertIn("C ", svg)

    def test_layer_order_and_visibility(self) -> None:
        data = json.loads(self.sample.read_text(encoding="utf-8"))
        data["layers"].append(
            {
                "id": "hidden_layer",
                "visible": False,
                "shapes": [
                    {
                        "id": "hidden_rect",
                        "type": "rect",
                        "x": 0,
                        "y": 0,
                        "width": 10,
                        "height": 10,
                        "fill": {"type": "solid", "color": "#000000"},
                    }
                ],
            }
        )
        data["layers"].append(
            {
                "id": "top_layer",
                "shapes": [
                    {
                        "id": "top_rect",
                        "type": "rect",
                        "x": 1,
                        "y": 1,
                        "width": 10,
                        "height": 10,
                        "fill": "none",
                        "stroke": {"color": "#111111", "width": 1, "join": "bevel", "cap": "square"},
                    }
                ],
            }
        )
        svg = export_svg(LineArtDocument.model_validate(data))
        self.assertLess(svg.index('id="main_layer"'), svg.index('id="top_layer"'))
        self.assertNotIn("hidden_rect", svg)
        self.assertIn('stroke-linejoin="bevel"', svg)
        self.assertIn('stroke-linecap="square"', svg)

    def test_lineart_paths_are_restricted(self) -> None:
        self.assertTrue(resolve_lineart_input("samples/lineart/icon_minimal.json", root=self.root).exists())
        self.assertEqual(
            resolve_lineart_output("generated/vector/out.svg", root=self.root).name,
            "out.svg",
        )
        self.assertEqual(
            resolve_lineart_raster_output("generated/images/out.png", root=self.root).name,
            "out.png",
        )
        with self.assertRaises(ValueError):
            resolve_lineart_input("samples/source/not_lineart.json", root=self.root)
        with self.assertRaises(ValueError):
            resolve_lineart_output("generated/images/out.svg", root=self.root)
        with self.assertRaises(ValueError):
            resolve_lineart_raster_output("generated/vector/out.png", root=self.root)

    def test_run_lineart_render_dry_run(self) -> None:
        out = run_lineart_render(
            Path("samples/lineart/icon_minimal.json"),
            Path("generated/vector/icon_minimal_test.svg"),
            root=self.root,
            dry_run=True,
            png_output=Path("generated/images/icon_minimal_test.png"),
        )
        self.assertEqual(out, self.output)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.png_output.exists())

    def test_run_lineart_render(self) -> None:
        out = run_lineart_render(
            Path("samples/lineart/icon_minimal.json"),
            Path("generated/vector/icon_minimal_test.svg"),
            root=self.root,
        )
        self.assertEqual(out, self.output)
        self.assertTrue(self.output.exists())
        self.assertIn("wave_01", self.output.read_text(encoding="utf-8"))

    @unittest.skipUnless(_has_svg_raster_backend(), "resvg-py or cairosvg is not installed")
    def test_run_lineart_render_png(self) -> None:
        out = run_lineart_render(
            Path("samples/lineart/icon_minimal.json"),
            Path("generated/vector/icon_minimal_test.svg"),
            root=self.root,
            png_output=Path("generated/images/icon_minimal_test.png"),
            png_width=64,
        )
        self.assertEqual(out, self.output)
        self.assertTrue(self.output.exists())
        self.assertTrue(self.png_output.exists())
        with Image.open(self.png_output) as image:
            self.assertEqual(image.size[0], 64)

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

    @unittest.skipUnless(_has_svg_raster_backend(), "resvg-py or cairosvg is not installed")
    def test_cli_lineart_render_png(self) -> None:
        code = main(
            [
                "lineart",
                "render",
                "samples/lineart/icon_minimal.json",
                "generated/vector/icon_minimal_test.svg",
                "--png",
                "generated/images/icon_minimal_test.png",
                "--png-width",
                "64",
            ]
        )
        self.assertEqual(code, 0)
        self.assertTrue(self.output.exists())
        self.assertTrue(self.png_output.exists())


if __name__ == "__main__":
    unittest.main()
