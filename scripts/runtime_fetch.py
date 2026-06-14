#!/usr/bin/env python3
"""GraphAssist runtime bootstrap: layout, binary/font fetch, manifest."""

from __future__ import annotations

import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_jsonc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # Strip // line comments, but not :// in URLs (https://, etc.)
    stripped = re.sub(r"(?<!:)//[^\n\r]*", "", text)
    return json.loads(stripped)


def platform_key() -> str | None:
    if sys.platform == "win32":
        return "win64"
    if sys.platform.startswith("linux"):
        return "linux"
    return None


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "graphassist-setup-runtime"})
    with urllib.request.urlopen(request, timeout=180) as response:
        dest.write_bytes(response.read())


def mirror_font_to_legacy(root: Path, dest: Path) -> None:
    legacy_dir = root / "assets/fonts"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    legacy = legacy_dir / dest.name
    if legacy.resolve() != dest.resolve():
        shutil.copy2(dest, legacy)


def fetch_binary(root: Path, runtime: Path, component: dict, *, force: bool = False) -> dict:
    plat = platform_key()
    record = {"id": component["id"], "kind": "binary", "present": False}
    if plat is None:
        record["note"] = f"unsupported platform: {sys.platform}"
        return record

    meta_path = root / ".rulesync/metadata/graphassist.json"
    version = json.loads(meta_path.read_text(encoding="utf-8"))["version"] if meta_path.is_file() else "unknown"
    record["version"] = version

    install_rel = component["install"].get(plat)
    release = component.get("release", {}).get(plat)
    if not install_rel or not release:
        record["note"] = "no release mapping for platform"
        return record

    dest = root / install_rel
    record["path"] = str(dest)
    asset = release["asset"]
    url = release["url_template"].format(version=version, asset=asset)

    if dest.is_file() and not force:
        record["present"] = True
        record["source"] = "cached"
        return record

    print(f"  binary: downloading {asset} (v{version})")
    try:
        download(url, dest)
    except (urllib.error.HTTPError, OSError) as exc:
        print(f"  binary: download failed ({exc})")
        print(f"    URL: {url}")
        return record

    if plat != "win64":
        dest.chmod(dest.stat().st_mode | 0o111)
    record["present"] = True
    record["source"] = "release"
    print(f"  binary: installed {dest}")
    return record


def fetch_font(root: Path, component: dict, *, force: bool = False) -> dict:
    record = {"id": component["id"], "kind": "font", "present": False}
    install = component.get("install", {})
    path_key = install.get("path")
    if not path_key:
        record["note"] = "install.path missing"
        return record

    dest = root / path_key
    record["path"] = str(dest)

    if dest.is_file() and not force:
        mirror_font_to_legacy(root, dest)
        record["present"] = True
        record["source"] = "cached"
        print(f"  font ({component['id']}): up to date ({dest.name})")
        return record

    release = component.get("release", {})
    if release.get("url"):
        print(f"  font ({component['id']}): downloading {dest.name}")
        try:
            download(release["url"], dest)
            record["present"] = True
            record["source"] = "download"
            license_url = release.get("license_url")
            if license_url:
                license_dest = dest.with_name(f"{dest.stem}-LICENSE")
                if not license_dest.is_file() or force:
                    try:
                        download(license_url, license_dest)
                    except (urllib.error.HTTPError, OSError) as exc:
                        print(f"  font ({component['id']}): license fetch skipped ({exc})")
            mirror_font_to_legacy(root, dest)
            print(f"  font ({component['id']}): installed {dest}")
            return record
        except (urllib.error.HTTPError, OSError) as exc:
            print(f"  font ({component['id']}): download failed ({exc})")

    plat = platform_key()
    for src_str in component.get("local_sources", {}).get(plat or "", []):
        src = Path(src_str)
        if src.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            mirror_font_to_legacy(root, dest)
            record["present"] = True
            record["source"] = f"local:{src}"
            print(f"  font ({component['id']}): copied from {src}")
            return record

    if component.get("optional"):
        print(f"  font ({component['id']}): skipped (optional, not available)")
        record["note"] = "optional, not available"
    else:
        print(f"  font ({component['id']}): not installed")
    return record


def fetch_components(root: Path, runtime: Path, *, force: bool = False) -> tuple[list[dict], dict]:
    manifest_path = root / ".rulesync/metadata/runtime-manifest.jsonc"
    if not manifest_path.is_file():
        return [], {}

    manifest = read_jsonc(manifest_path)
    records: list[dict] = []
    for component in manifest.get("components", []):
        if component.get("enabled") is False:
            continue
        kind = component.get("kind")
        if kind == "binary":
            records.append(fetch_binary(root, runtime, component, force=force))
        elif kind == "font":
            records.append(fetch_font(root, component, force=force))
    return records, manifest


def write_font_notices(root: Path, runtime: Path, manifest: dict) -> None:
    lines = [
        "# Font notices",
        "",
        "Auto-generated by `scripts/setup-runtime` from `.rulesync/metadata/runtime-manifest.jsonc`.",
        "Do not edit by hand; re-run setup after manifest changes.",
        "",
        "| File | ID | Copyright | License | Source |",
        "|------|-----|-----------|---------|--------|",
    ]
    for component in manifest.get("components", []):
        if component.get("kind") != "font":
            continue
        install_path = component.get("install", {}).get("path", "")
        filename = Path(install_path).name if install_path else "—"
        release = component.get("release", {})
        copyright_text = release.get("copyright", "—")
        license_name = release.get("license_name", "—")
        source_url = release.get("source_url", "—")
        lines.append(
            f"| `{filename}` | `{component['id']}` | {copyright_text} | {license_name} | {source_url} |"
        )
    body = "\n".join(lines) + "\n"
    for dest in (root / "assets/fonts/NOTICES.md", runtime / "assets/fonts/NOTICES.md"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")


def write_manifest(root: Path, runtime: Path, components: list[dict]) -> None:
    record = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runtime_root": str(runtime),
        "components": components,
    }
    local_manifest = runtime / "manifest.local.json"
    local_manifest.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    root = repo_root()
    runtime = Path(
        __import__("os").environ.get("GRAPHASSIST_RUNTIME", str(root / "runtime"))
    ).resolve()
    force = "--force" in sys.argv[1:]

    for sub in ("bin", "assets/fonts", "assets/weights/bg-removal"):
        (runtime / sub).mkdir(parents=True, exist_ok=True)
    (root / "assets/fonts").mkdir(parents=True, exist_ok=True)

    print("GraphAssist runtime setup")
    print(f"  runtime: {runtime}")

    meta_path = root / ".rulesync/metadata/graphassist.json"
    tool_version = "unknown"
    if meta_path.is_file():
        tool_version = json.loads(meta_path.read_text(encoding="utf-8"))["version"]
    print(f"  tool version (metadata): {tool_version}")

    components, manifest = fetch_components(root, runtime, force=force)
    write_manifest(root, runtime, components)
    if manifest:
        write_font_notices(root, runtime, manifest)
        print(f"  font notices: {root / 'assets/fonts/NOTICES.md'}")

    binary = next((c for c in components if c.get("id") == "graphassist"), None)
    if binary and binary.get("present"):
        print("  binary: OK")
    else:
        print("  binary: not installed")
        print("    Run with network to fetch from GitHub Releases, or:")
        print("    uv run graphassist --version")

    fonts = [c for c in components if c.get("kind") == "font"]
    installed_fonts = [c["id"] for c in fonts if c.get("present")]
    if installed_fonts:
        print(f"  fonts: {', '.join(installed_fonts)}")
    else:
        print("  fonts: none installed")

    print(f"  manifest: {runtime / 'manifest.local.json'}")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
