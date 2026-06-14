"""Asset catalog fetch tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from graphassist.engine.catalog_fetch import (
    fetch_catalog_asset,
    load_catalog_manifest,
    rasterize_svg,
    write_catalog_notices,
)


class CatalogFetchTest(unittest.TestCase):
    def test_load_catalog_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = load_catalog_manifest(root)
        self.assertEqual(manifest.get("version"), "1.0")
        self.assertGreaterEqual(len(manifest.get("assets", [])), 1)

    def test_fetch_and_rasterize_local_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            svg = root / "runtime/assets/catalog/svg/test.svg"
            svg.parent.mkdir(parents=True, exist_ok=True)
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<rect width="10" height="10" fill="#ff0000"/></svg>',
                encoding="utf-8",
            )
            asset = {
                "id": "test-asset",
                "enabled": True,
                "release": {"url": "https://example.invalid/test.svg"},
                "install": {
                    "path": "runtime/assets/catalog/svg/test.svg",
                    "mirror_svg": "samples/source/catalog/test.svg",
                    "mirror_raster": "samples/source/catalog/test.png",
                },
                "rasterize": {"width": 32, "backend": "resvg"},
            }
            with patch("graphassist.engine.catalog_fetch.download") as mock_dl:
                record = fetch_catalog_asset(root, asset, force=False)
                mock_dl.assert_not_called()
            self.assertTrue(record["present"])
            png = root / "samples/source/catalog/test.png"
            self.assertTrue(png.is_file())
            mirrored = root / "samples/source/catalog/test.svg"
            self.assertTrue(mirrored.is_file())

    def test_fetch_local_seed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed = root / "assets/catalog/seeds/panel.svg"
            seed.parent.mkdir(parents=True, exist_ok=True)
            seed.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">'
                '<rect width="8" height="8" fill="#111"/></svg>',
                encoding="utf-8",
            )
            asset = {
                "id": "ui-panel-test",
                "enabled": True,
                "release": {"local": "assets/catalog/seeds/panel.svg"},
                "install": {
                    "path": "runtime/assets/catalog/svg/ui-panel-test.svg",
                    "mirror_svg": "samples/source/catalog/ui-panel-test.svg",
                    "mirror_raster": "samples/source/catalog/ui-panel-test.png",
                },
                "rasterize": {"width": 16},
            }
            record = fetch_catalog_asset(root, asset, force=True)
            self.assertTrue(record["present"])
            self.assertEqual(record.get("source"), "local")

    def test_present_without_raster_width(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed = root / "assets/catalog/seeds/icon.svg"
            seed.parent.mkdir(parents=True, exist_ok=True)
            seed.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4">'
                '<rect width="4" height="4"/></svg>',
                encoding="utf-8",
            )
            asset = {
                "id": "svg-only",
                "enabled": True,
                "release": {"local": "assets/catalog/seeds/icon.svg"},
                "install": {
                    "path": "runtime/assets/catalog/svg/svg-only.svg",
                    "mirror_svg": "samples/source/catalog/svg-only.svg",
                    "mirror_raster": "samples/source/catalog/svg-only.png",
                },
            }
            record = fetch_catalog_asset(root, asset, force=True)
            self.assertTrue(record["present"])
            self.assertNotIn("mirror_raster", record)

    def test_rasterize_failure_does_not_crash_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            svg = root / "runtime/assets/catalog/svg/bad.svg"
            svg.parent.mkdir(parents=True, exist_ok=True)
            svg.write_text("not valid svg", encoding="utf-8")
            asset = {
                "id": "bad-svg",
                "enabled": True,
                "release": {"url": "https://example.invalid/bad.svg"},
                "install": {
                    "path": "runtime/assets/catalog/svg/bad.svg",
                    "mirror_raster": "samples/source/catalog/bad.png",
                },
                "rasterize": {"width": 32},
            }
            with patch("graphassist.engine.catalog_fetch.download"):
                record = fetch_catalog_asset(root, asset, force=False)
            self.assertFalse(record["present"])

    def test_rasterize_svg_requires_backend_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            svg = root / "a.svg"
            png = root / "a.png"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4">'
                '<rect width="4" height="4"/></svg>',
                encoding="utf-8",
            )
            try:
                import resvg_py  # noqa: F401
            except ImportError:
                with self.assertRaises(RuntimeError):
                    rasterize_svg(svg, png, width=16)
            else:
                rasterize_svg(svg, png, width=16)
                self.assertTrue(png.is_file())

    def test_write_catalog_notices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "runtime"
            manifest = {
                "assets": [
                    {
                        "id": "x",
                        "enabled": True,
                        "copyright": "PD",
                        "license_name": "CC0",
                        "source_url": "https://example.test",
                    }
                ]
            }
            write_catalog_notices(root, runtime, manifest)
            text = (root / "assets/catalog/NOTICES.md").read_text(encoding="utf-8")
            self.assertIn("x", text)
            self.assertIn("CC0", text)


if __name__ == "__main__":
    unittest.main()
