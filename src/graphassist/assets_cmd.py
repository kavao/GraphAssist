"""CLI: graphassist assets fetch|list."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from graphassist.engine.catalog_fetch import (
    fetch_catalog,
    load_catalog_manifest,
    write_catalog_notices,
)
from graphassist.schema.catalog import known_catalog_ids
from graphassist.schema.paths import project_root, runtime_root


def materialize_catalog(
    *,
    force: bool = False,
    ids: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Fetch catalog assets. Returns (installed_ids, missing_ids)."""
    root = project_root()
    runtime = runtime_root(root=root)

    records, manifest = fetch_catalog(root, force=force, ids=ids)
    if manifest:
        write_catalog_notices(root, runtime, manifest)

    installed = [r["id"] for r in records if r.get("present")]
    missing = [r["id"] for r in records if not r.get("present")]
    return installed, missing


def run_assets_fetch(
    *,
    force: bool = False,
    ids: list[str] | None = None,
) -> int:
    if ids:
        unknown = [asset_id for asset_id in ids if asset_id not in known_catalog_ids()]
        if unknown:
            print(f"catalog unknown ids: {', '.join(unknown)}", file=sys.stderr)
            return 1

    installed, missing = materialize_catalog(force=force, ids=ids)
    if installed:
        print(f"catalog: {', '.join(installed)}")
    if missing:
        print(f"catalog missing: {', '.join(missing)}", file=sys.stderr)
    manifest = load_catalog_manifest(project_root())
    if ids and manifest and not installed and not missing:
        print("catalog: no assets matched", file=sys.stderr)
        return 1
    if manifest and not ids and not installed and not missing:
        print("catalog: no assets matched")
    return 0 if not missing else 1


def run_assets_materialize(
    *,
    force: bool = False,
    ids: list[str] | None = None,
) -> int:
    return run_assets_fetch(force=force, ids=ids)


def run_assets_list(*, fmt: str = "text") -> int:
    root = project_root()
    manifest = load_catalog_manifest(root)
    assets = [a for a in manifest.get("assets", []) if a.get("enabled") is not False]
    if fmt == "json":
        print(json.dumps({"assets": assets}, ensure_ascii=False, indent=2))
        return 0
    for asset in assets:
        install = asset.get("install", {})
        print(
            f"{asset['id']}\t{asset.get('license_name', '')}\t"
            f"{install.get('mirror_raster', install.get('path', ''))}"
        )
    return 0
