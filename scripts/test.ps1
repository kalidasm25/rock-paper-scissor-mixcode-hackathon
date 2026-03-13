$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Run scripts/setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\python.exe -m pytest -q
