param(
  [string]$OutputName
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not $OutputName) {
  $timestamp = Get-Date -Format "yyyyMMdd_HHmm"
  $OutputName = "NeonRun_share_$timestamp.zip"
}

$tempDir = Join-Path $env:TEMP ("NeonRun_share_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDir | Out-Null

$include = @(
  "index.html",
  "README.md"
)

foreach ($file in $include) {
  $src = Join-Path $root $file
  if (Test-Path $src) {
    Copy-Item -Path $src -Destination (Join-Path $tempDir $file)
  }
}

$zipPath = Join-Path $root $OutputName
if (Test-Path $zipPath) {
  Remove-Item $zipPath -Force
}

Compress-Archive -Path (Join-Path $tempDir "*") -DestinationPath $zipPath -Force
Remove-Item $tempDir -Recurse -Force

Write-Host "Created:" $zipPath
