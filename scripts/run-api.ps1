param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Run scripts/setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\python.exe main.py --api --host $HostName --port $Port
