#!/usr/bin/env python3
"""GraphAssist runtime bootstrap: layout, optional GitHub Release download, manifest."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_jsonc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    stripped = re.sub(r"//.*", "", text)
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
    with urllib.request.urlopen(request, timeout=120) as response:
        dest.write_bytes(response.read())


def fetch_binary(root: Path, runtime: Path, *, force: bool = False) -> bool:
    meta_path = root / ".rulesync/metadata/graphassist.json"
    manifest_path = root / ".rulesync/metadata/runtime-manifest.jsonc"
    if not meta_path.is_file() or not manifest_path.is_file():
        return False

    version = json.loads(meta_path.read_text(encoding="utf-8"))["version"]
    manifest = read_jsonc(manifest_path)
    plat = platform_key()
    if plat is None:
        print(f"  binary: skip download (unsupported platform: {sys.platform})")
        return False

    component = next((c for c in manifest["components"] if c["id"] == "graphassist"), None)
    if component is None:
        return False

    install_rel = component["install"].get(plat)
    release = component.get("release", {}).get(plat)
    if not install_rel or not release:
        return False

    dest = root / install_rel
    asset = release["asset"]
    url_template = release["url_template"]
    url = url_template.format(version=version, asset=asset)

    local_manifest = runtime / "manifest.local.json"
    installed_version: str | None = None
    if local_manifest.is_file():
        try:
            local = json.loads(local_manifest.read_text(encoding="utf-8"))
            for item in local.get("components", []):
                if item.get("id") == "graphassist":
                    installed_version = item.get("version")
                    break
        except json.JSONDecodeError:
            pass

    if dest.is_file() and not force and installed_version == version:
        print(f"  binary: up to date ({dest})")
        return True

    print(f"  binary: downloading {asset} (v{version})")
    try:
        download(url, dest)
    except urllib.error.HTTPError as exc:
        print(f"  binary: download failed ({exc.code} {exc.reason})")
        print(f"    URL: {url}")
        return False
    except OSError as exc:
        print(f"  binary: download failed ({exc})")
        return False

    if plat != "win64":
        dest.chmod(dest.stat().st_mode | 0o111)
    print(f"  binary: installed {dest}")
    return True


def write_manifest(root: Path, runtime: Path) -> None:
    meta_path = root / ".rulesync/metadata/graphassist.json"
    tool_version = "unknown"
    if meta_path.is_file():
        tool_version = json.loads(meta_path.read_text(encoding="utf-8"))["version"]

    plat = platform_key()
    if plat == "win64":
        bin_path = runtime / "bin/graphassist.exe"
    else:
        bin_path = runtime / "bin/graphassist"

    record = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runtime_root": str(runtime),
        "components": [
            {
                "id": "graphassist",
                "kind": "binary",
                "version": tool_version,
                "path": str(bin_path),
                "present": bin_path.is_file(),
            }
        ],
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

    print("GraphAssist runtime setup")
    print(f"  runtime: {runtime}")

    meta_path = root / ".rulesync/metadata/graphassist.json"
    tool_version = "unknown"
    if meta_path.is_file():
        tool_version = json.loads(meta_path.read_text(encoding="utf-8"))["version"]
    print(f"  tool version (metadata): {tool_version}")

    fetch_binary(root, runtime, force=force)
    write_manifest(root, runtime)

    bin_win = runtime / "bin/graphassist.exe"
    bin_unix = runtime / "bin/graphassist"
    if bin_win.is_file() or bin_unix.is_file():
        print("  binary: OK")
    else:
        print("  binary: not installed")
        print("    Run with network to fetch from GitHub Releases, or:")
        print("    uv run graphassist --version")

    print(f"  manifest: {runtime / 'manifest.local.json'}")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
