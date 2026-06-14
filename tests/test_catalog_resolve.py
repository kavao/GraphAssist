"""Catalog asset id resolution tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from graphassist.engine.catalog_resolve import resolve_catalog_asset
from graphassist.engine.executor import execute_job
from graphassist.schema.catalog import validate_catalog_id
from graphassist.schema.job import ImageJob
from graphassist.schema.ops import CompositeOp
from graphassist.schema.paths import project_root


class CatalogResolveTest(unittest.TestCase):
    def test_validate_catalog_id_rejects_unknown(self) -> None:
        with self.assertRaises(ValueError):
            validate_catalog_id("not-in-catalog")

    def test_composite_overlay_asset_schema(self) -> None:
        op = CompositeOp.model_validate(
            {
                "type": "composite",
                "overlay_asset": "ornament-fleur-de-lis-simple",
                "x": 0,
                "y": 0,
            }
        )
        self.assertEqual(op.overlay_asset, "ornament-fleur-de-lis-simple")
        self.assertIsNone(op.overlay)

    def test_composite_rejects_both_overlay_sources(self) -> None:
        with self.assertRaises(ValueError):
            CompositeOp.model_validate(
                {
                    "type": "composite",
                    "overlay": "samples/source/x.png",
                    "overlay_asset": "ornament-fleur-de-lis-simple",
                    "x": 0,
                    "y": 0,
                }
            )

    def test_resolve_with_local_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_dir = root / ".rulesync/metadata"
            manifest_dir.mkdir(parents=True)
            manifest_dir.joinpath("asset-catalog.jsonc").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "assets": [
                            {
                                "id": "test-badge",
                                "kind": "png",
                                "enabled": True,
                                "install": {
                                    "path": "runtime/assets/catalog/png/test-badge.png",
                                    "mirror": "samples/source/catalog/test-badge.png",
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            png = root / "samples/source/catalog/test-badge.png"
            png.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(png)

            resolved = resolve_catalog_asset(
                "test-badge",
                root=root,
                auto_materialize=False,
            )
            self.assertEqual(resolved, png)

    def test_overlay_asset_job(self) -> None:
        root = project_root()
        png = root / "samples/source/catalog/ornament-fleur-de-lis-simple.png"
        if not png.is_file():
            self.skipTest("catalog not materialized")

        out = root / "generated/images/test_overlay_asset_job.png"
        if out.exists():
            out.unlink()

        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input": "samples/source/demo_text_base.png",
                "output": "generated/images/test_overlay_asset_job.png",
                "operations": [
                    {
                        "type": "composite",
                        "overlay_asset": "ornament-fleur-de-lis-simple",
                        "x": 8,
                        "y": 8,
                    }
                ],
            }
        )
        execute_job(job, root=root, dry_run=False)
        self.assertTrue(out.is_file())
        if out.exists():
            out.unlink()

    def test_input_asset_job(self) -> None:
        root = project_root()
        if not (root / "samples/source/catalog/ui-panel-dark.png").is_file():
            self.skipTest("ui-panel-dark not materialized")

        out = root / "generated/images/test_input_asset_job.png"
        if out.exists():
            out.unlink()

        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input_asset": "ui-panel-dark",
                "output": "generated/images/test_input_asset_job.png",
                "operations": [
                    {
                        "type": "composite",
                        "overlay_asset": "ornament-fleur-de-lis-simple",
                        "x": 100,
                        "y": 100,
                    }
                ],
            }
        )
        execute_job(job, root=root, dry_run=False)
        self.assertTrue(out.is_file())
        if out.exists():
            out.unlink()

    def test_rejects_both_input_sources(self) -> None:
        with self.assertRaises(ValueError):
            ImageJob.model_validate(
                {
                    "version": "1.0",
                    "input": "samples/source/demo_text_base.png",
                    "input_asset": "ui-panel-dark",
                    "output": "generated/images/x.png",
                    "operations": [],
                }
            )

    def test_dry_run_input_asset_skips_auto_materialize(self) -> None:
        root = project_root()
        job = ImageJob.model_validate(
            {
                "version": "1.0",
                "input_asset": "ui-panel-dark",
                "output": "generated/images/dry_run_input_asset.png",
                "operations": [],
            }
        )
        with patch("graphassist.assets_cmd.materialize_catalog") as mock_mat:
            job.resolved_input(root=root, must_exist=False)
            mock_mat.assert_not_called()


if __name__ == "__main__":
    unittest.main()
