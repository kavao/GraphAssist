#Requires -Version 5.1
<#
.SYNOPSIS
  GraphAssist runtime bootstrap (idempotent, re-runnable).
#>
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pyArgs = @("$Root/scripts/runtime_fetch.py")
if ($Force) { $pyArgs += "--force" }
& python @pyArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
