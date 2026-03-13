$ErrorActionPreference = "Stop"

$SystemPython = $null

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python --version | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $SystemPython = "python"
    }
}

if (-not $SystemPython) {
    $knownPaths = @(
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe"
    )

    foreach ($path in $knownPaths) {
        if (Test-Path $path) {
            $SystemPython = $path
            break
        }
    }
}

if (-not $SystemPython) {
    Write-Host "Python was not found. Install Python 3.11+ and rerun this script." -ForegroundColor Red
    exit 1
}

& $SystemPython -m venv .venv
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment creation failed. Ensure Python is installed correctly." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Setup complete. Activate with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
