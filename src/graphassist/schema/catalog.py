"""Catalog asset id validation (whitelist from manifest)."""

from __future__ import annotations

import re
from pathlib import Path

from graphassist.engine.catalog_fetch import load_catalog_manifest
from graphassist.schema.paths import project_root

CATALOG_ID_RE = re.compile(r"^[a-z0-9-]+$")


def known_catalog_ids(*, root: Path | None = None) -> frozenset[str]:
    root = root or project_root()
    manifest = load_catalog_manifest(root)
    return frozenset(
        asset["id"]
        for asset in manifest.get("assets", [])
        if asset.get("enabled") is not False and "id" in asset
    )


def validate_catalog_id(asset_id: str, *, root: Path | None = None) -> str:
    if not CATALOG_ID_RE.fullmatch(asset_id):
        raise ValueError(f"invalid catalog asset id: {asset_id}")
    if asset_id not in known_catalog_ids(root=root):
        raise ValueError(f"unknown catalog asset id: {asset_id}")
    return asset_id
