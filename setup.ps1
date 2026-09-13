$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path ".venv/Scripts/python.exe")) {
        py -3.11 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Instale Python 3.11 com Tkinter e tente novamente." }
    }
    & ".venv/Scripts/python.exe" -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as dependencias." }
} finally { Pop-Location }
