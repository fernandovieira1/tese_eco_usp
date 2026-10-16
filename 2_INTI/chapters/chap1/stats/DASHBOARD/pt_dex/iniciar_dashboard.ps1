$ErrorActionPreference = 'Stop'
$dashboardPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$dashboardApp = Join-Path $PSScriptRoot 'app.py'
if (-not (Test-Path -LiteralPath $dashboardPython)) {
    throw 'Ambiente ausente. Siga os comandos de instalação do README.md nesta pasta.'
}
& $dashboardPython -m streamlit run $dashboardApp
exit $LASTEXITCODE
