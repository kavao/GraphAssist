"""Resolve catalog asset ids to materialized mirror paths."""

from __future__ import annotations

from pathlib import Path

from graphassist.engine.catalog_fetch import load_catalog_manifest


def _find_catalog_asset(manifest: dict, asset_id: str) -> dict | None:
    for asset in manifest.get("assets", []):
        if asset.get("id") == asset_id and asset.get("enabled") is not False:
            return asset
    return None


def catalog_mirror_rel(asset: dict) -> str:
    install = asset.get("install", {})
    rel = install.get("mirror_raster") or install.get("mirror")
    if not rel:
        raise ValueError(f"catalog asset {asset.get('id')} has no mirror path configured")
    return rel


def resolve_catalog_asset(
    asset_id: str,
    *,
    root: Path,
    must_exist: bool = True,
    auto_materialize: bool = True,
) -> Path:
    manifest = load_catalog_manifest(root)
    asset = _find_catalog_asset(manifest, asset_id)
    if asset is None:
        raise ValueError(f"unknown catalog asset id: {asset_id}")

    path = root / catalog_mirror_rel(asset)
    if path.is_file():
        return path

    if auto_materialize:
        from graphassist.assets_cmd import materialize_catalog

        _, missing = materialize_catalog(ids=[asset_id])
        if asset_id not in missing and path.is_file():
            return path

    if must_exist:
        raise FileNotFoundError(
            f"catalog asset not materialized: {asset_id} ({path.relative_to(root).as_posix()}). "
            "Run graphassist assets fetch or batch assets.materialize"
        )
    return path
