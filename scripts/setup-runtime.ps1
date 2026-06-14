#Requires -Version 5.1
<#
.SYNOPSIS
  GraphAssist runtime bootstrap (idempotent, re-runnable).

  Creates runtime/ layout, reads .rulesync/metadata/runtime-manifest.jsonc,
  and prepares bin/fonts/weights directories. Download URLs can be wired later.
#>
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Runtime = if ($env:GRAPHASSIST_RUNTIME) { $env:GRAPHASSIST_RUNTIME } else { Join-Path $Root "runtime" }

$dirs = @(
    (Join-Path $Runtime "bin"),
    (Join-Path $Runtime "assets/fonts"),
    (Join-Path $Runtime "assets/weights"),
    (Join-Path $Runtime "assets/weights/bg-removal")
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

$metaPath = Join-Path $Root ".rulesync/metadata/graphassist.json"
$toolVersion = "unknown"
if (Test-Path $metaPath) {
    $toolVersion = (Get-Content $metaPath -Raw -Encoding UTF8 | ConvertFrom-Json).version
}

$localManifest = Join-Path $Runtime "manifest.local.json"
$record = [ordered]@{
    updated_at = (Get-Date).ToUniversalTime().ToString("o")
    runtime_root = $Runtime
    components = @(
        [ordered]@{
            id = "graphassist"
            kind = "binary"
            version = $toolVersion
            path = (Join-Path $Runtime "bin/graphassist.exe")
            present = (Test-Path (Join-Path $Runtime "bin/graphassist.exe"))
        }
    )
}
$record | ConvertTo-Json -Depth 6 | Set-Content -Path $localManifest -Encoding UTF8

Write-Host "GraphAssist runtime setup"
Write-Host "  runtime: $Runtime"
Write-Host "  tool version (metadata): $toolVersion"
$bin = Join-Path $Runtime "bin/graphassist.exe"
if (Test-Path $bin) {
    Write-Host "  binary: OK $bin"
} else {
    Write-Host "  binary: not installed"
    Write-Host "    Place graphassist.exe manually, or run from source:"
    Write-Host "    uv run python tools/graphassist/graphassist.py --version"
}
Write-Host "  manifest: $localManifest"
Write-Host "Done."
