$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path ".venv/Scripts/python.exe")) { & "./setup.ps1" }
    & ".venv/Scripts/python.exe" app.py
    if ($LASTEXITCODE -ne 0) { throw "O aplicativo encerrou com erro." }
} finally { Pop-Location }
