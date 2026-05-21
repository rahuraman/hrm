# Initialize Git repository for HRM project
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

function Find-Git {
    $candidates = @(
        "git",
        "$env:ProgramFiles\Git\cmd\git.exe",
        "${env:ProgramFiles(x86)}\Git\cmd\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
    )
    foreach ($c in $candidates) {
        if (Get-Command $c -ErrorAction SilentlyContinue) {
            return (Get-Command $c).Source
        }
        if (Test-Path $c) { return $c }
    }
    return $null
}

$git = Find-Git
if (-not $git) {
    Write-Host "Git is not installed or not on PATH." -ForegroundColor Red
    Write-Host "Install from: https://git-scm.com/download/win"
    Write-Host "Then re-run: .\init-git.ps1"
    exit 1
}

Set-Location $root

if (Test-Path ".git") {
    Write-Host "Git repository already exists in $root"
} else {
    & $git init
    Write-Host "Initialized git repository."
}

& $git add .
$status = & $git status --porcelain
if (-not $status) {
    Write-Host "Nothing to commit (working tree clean)."
    exit 0
}

# Use local identity if global git user is not configured
if (-not (& $git config user.email 2>$null)) {
    $env:GIT_AUTHOR_NAME = "HRM Developer"
    $env:GIT_AUTHOR_EMAIL = "developer@local"
    $env:GIT_COMMITTER_NAME = $env:GIT_AUTHOR_NAME
    $env:GIT_COMMITTER_EMAIL = $env:GIT_AUTHOR_EMAIL
    Write-Host "Using local author identity (set git config user.name/email for your own identity)."
}

& $git commit -m @"
Initial commit: HRM modular report generator

- data_layer: CSV loading
- report: onboarding loss analytics (8 hrs/day)
- report_html: HTML dashboard
- main.py entry point
"@

Write-Host "Done. Repository ready at $root" -ForegroundColor Green
& $git log -1 --oneline
