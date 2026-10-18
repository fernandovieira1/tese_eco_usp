$ErrorActionPreference = 'Stop'
$appDirectory = Split-Path -Parent $PSScriptRoot
$repoDirectory = $appDirectory
while (-not (Test-Path -LiteralPath (Join-Path $repoDirectory '2_INTI/RESEARCH_PROTOCOL.md'))) {
    $repoDirectory = Split-Path -Parent $repoDirectory
    if (-not $repoDirectory) { throw 'Raiz do repositório não encontrada.' }
}
$pythonProject = Join-Path $repoDirectory '.venv/Scripts/python.exe'
$runtimeDirectory = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies'
$nodeRuntime = Join-Path $runtimeDirectory 'node/bin/node.exe'
$pythonRuntime = Join-Path $runtimeDirectory 'python/python.exe'
$moduleDirectory = Join-Path $PSScriptRoot 'node_modules'
if (-not (Test-Path -LiteralPath $moduleDirectory)) {
    New-Item -ItemType Junction -Path $moduleDirectory -Target (Join-Path $runtimeDirectory 'node/node_modules') | Out-Null
}
Push-Location $appDirectory
try {
    & $pythonRuntime -X utf8 (Join-Path $PSScriptRoot 'extrair_candidatas.py')
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao ler candidatas do Excel anterior.' }
    foreach ($scriptName in @('estimar_fe.py','preparar_excel_fe.py')) {
        & $pythonProject -X utf8 (Join-Path $PSScriptRoot $scriptName)
        if ($LASTEXITCODE -ne 0) { throw "Falha em $scriptName" }
    }
    & $nodeRuntime (Join-Path $PSScriptRoot 'exportar_fe.mjs')
    if ($LASTEXITCODE -ne 0) { throw 'Falha na exportação Excel.' }
    & $pythonRuntime -X utf8 (Join-Path $PSScriptRoot 'verificar_fe.py')
    if ($LASTEXITCODE -ne 0) { throw 'Falha na verificação final.' }
}
finally { Pop-Location }
