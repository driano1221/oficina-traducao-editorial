$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path ".venv/Scripts/python.exe")) { & "./setup.ps1" }
    & ".venv/Scripts/python.exe" -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias de build." }
    & ".venv/Scripts/python.exe" -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Testes falharam. Build interrompido." }
    & ".venv/Scripts/python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name OficinaTraducao --add-data "glossario.json;." --add-data "LICENSE;." --add-data "NOTICE.md;." app.py
    if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar executavel." }
    Write-Host "Executavel local: dist/OficinaTraducao.exe"
    Write-Host "Antes de redistribuir, leia docs/BUILD_E_DISTRIBUICAO.md."
} finally { Pop-Location }
