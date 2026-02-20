param(
  [Parameter(Mandatory = $true)]
  [string]$RepoUrl
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path "index.html")) {
  throw "index.html が見つかりません。"
}

if (-not (Test-Path ".git")) {
  git init
}

git add .
git commit -m "Prepare GitHub Pages deploy" 2>$null

$hasOrigin = git remote 2>$null | Select-String -Pattern "^origin$"
if (-not $hasOrigin) {
  git remote add origin $RepoUrl
} else {
  git remote set-url origin $RepoUrl
}

git branch -M main
git push -u origin main

Write-Host "Pushed to main."
Write-Host "GitHubで Settings > Pages > Source を 'GitHub Actions' にすると公開されます。"
