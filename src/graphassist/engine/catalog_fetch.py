"""Asset catalog fetch, mirror, and optional SVG rasterize."""

from __future__ import annotations

import json
import re
import shutil
import urllib.error
import urllib.request
from pathlib import Path


def read_jsonc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    stripped = re.sub(r"(?<!:)//[^\n\r]*", "", text)
    return json.loads(stripped)


def load_catalog_manifest(root: Path) -> dict:
    path = root / ".rulesync/metadata/asset-catalog.jsonc"
    if not path.is_file():
        return {}
    return read_jsonc(path)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "graphassist-setup-runtime"})
    with urllib.request.urlopen(request, timeout=180) as response:
        dest.write_bytes(response.read())


def rasterize_svg(svg_path: Path, png_path: Path, *, width: int) -> None:
    svg_text = svg_path.read_text(encoding="utf-8")
    png_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import resvg_py

        try:
            png_path.write_bytes(resvg_py.svg_to_bytes(svg_string=svg_text, width=width))
            return
        except Exception as exc:
            raise RuntimeError(f"resvg-py rasterize failed for {svg_path.name}") from exc
    except ImportError:
        pass

    try:
        import cairosvg
    except ImportError as exc:
        raise RuntimeError(
            "resvg-py (recommended) or cairosvg is required to rasterize catalog SVG. "
            "Install with: uv sync --extra catalog"
        ) from exc

    try:
        cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), write_to=str(png_path), output_width=width)
    except Exception as exc:
        raise RuntimeError(f"cairosvg rasterize failed for {svg_path.name}") from exc


def _mirror_file(src: Path, dest_rel: str, *, root: Path) -> Path | None:
    if not dest_rel:
        return None
    dest = root / dest_rel
    if src.resolve() == dest.resolve():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def fetch_catalog_asset(root: Path, asset: dict, *, force: bool = False) -> dict:
    record: dict = {"id": asset["id"], "kind": "catalog", "present": False}
    if asset.get("enabled") is False:
        record["note"] = "disabled"
        return record

    install = asset.get("install", {})
    path_key = install.get("path")
    if not path_key:
        record["note"] = "install.path missing"
        return record

    dest = root / path_key
    mirror_svg = install.get("mirror_svg")
    mirror = install.get("mirror")
    mirror_raster = install.get("mirror_raster") or mirror
    record["path"] = str(dest)

    rasterize = asset.get("rasterize", {})
    raster_width = rasterize.get("width")
    need_acquire = force or not dest.is_file()

    if need_acquire:
        release = asset.get("release", {})
        local = release.get("local")
        url = release.get("url")
        if local:
            src = root / local
            if not src.is_file():
                record["note"] = f"release.local missing: {local}"
                return record
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            record["source"] = "local"
            print(f"  catalog ({asset['id']}): installed from {local}")
        elif url:
            print(f"  catalog ({asset['id']}): downloading {dest.name}")
            try:
                download(url, dest)
                record["source"] = "download"
            except (urllib.error.HTTPError, OSError) as exc:
                print(f"  catalog ({asset['id']}): download failed ({exc})")
                return record
        else:
            record["note"] = "release.url or release.local missing"
            return record
    else:
        record["source"] = "cached"
        print(f"  catalog ({asset['id']}): up to date ({dest.name})")

    license_url = asset.get("release", {}).get("license_url")
    if license_url:
        license_dest = dest.with_name(f"{dest.stem}-LICENSE")
        if force or not license_dest.is_file():
            try:
                download(license_url, license_dest)
            except (urllib.error.HTTPError, OSError) as exc:
                print(f"  catalog ({asset['id']}): license fetch skipped ({exc})")

    mirrored_svg = _mirror_file(dest, mirror_svg, root=root) if mirror_svg else None
    if mirrored_svg:
        record["mirror_svg"] = str(mirrored_svg)

    png_ready = False
    if mirror_raster and raster_width and dest.suffix.lower() == ".svg":
        png_path = root / mirror_raster
        need_raster = force or not png_path.is_file()
        if need_raster:
            try:
                rasterize_svg(dest, png_path, width=int(raster_width))
                png_ready = True
                print(f"  catalog ({asset['id']}): rasterized {png_path.name}")
            except (RuntimeError, OSError) as exc:
                print(f"  catalog ({asset['id']}): rasterize failed ({exc})")
        else:
            png_ready = True
        if png_ready:
            record["mirror_raster"] = str(png_path)
    elif mirror_raster and dest.suffix.lower() != ".svg":
        png_mirror = _mirror_file(dest, mirror_raster, root=root)
        if png_mirror:
            record["mirror_raster"] = str(png_mirror)
            png_ready = True

    needs_raster_png = bool(mirror_raster and raster_width and dest.suffix.lower() == ".svg")
    record["present"] = dest.is_file() and (not needs_raster_png or png_ready)
    if record["present"]:
        print(f"  catalog ({asset['id']}): installed")
    return record


def fetch_catalog(
    root: Path,
    *,
    force: bool = False,
    ids: list[str] | None = None,
) -> tuple[list[dict], dict]:
    manifest = load_catalog_manifest(root)
    if not manifest:
        return [], {}

    records: list[dict] = []
    for asset in manifest.get("assets", []):
        if ids is not None and asset.get("id") not in ids:
            continue
        records.append(fetch_catalog_asset(root, asset, force=force))
    return records, manifest


def write_catalog_notices(root: Path, runtime: Path, manifest: dict) -> None:
    lines = [
        "# Catalog asset notices",
        "",
        "Auto-generated by setup-runtime / assets fetch from "
        "`.rulesync/metadata/asset-catalog.jsonc`.",
        "",
        "| ID | Copyright | License | Source |",
        "|----|-----------|---------|--------|",
    ]
    for asset in manifest.get("assets", []):
        if asset.get("enabled") is False:
            continue
        lines.append(
            f"| `{asset['id']}` | {asset.get('copyright', '—')} | "
            f"{asset.get('license_name', '—')} | {asset.get('source_url', '—')} |"
        )
    body = "\n".join(lines) + "\n"
    for dest in (root / "assets/catalog/NOTICES.md", runtime / "assets/catalog/NOTICES.md"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
