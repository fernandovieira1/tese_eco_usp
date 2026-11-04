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
$modulesDirectory = Join-Path $PSScriptRoot 'node_modules'
if (-not (Test-Path -LiteralPath $modulesDirectory)) {
    New-Item -ItemType Junction -Path $modulesDirectory -Target (Join-Path $runtimeDirectory 'node/node_modules') | Out-Null
}
Push-Location $appDirectory
try {
    foreach ($scriptName in @('estimar_robustez.py','preparar_excel.py')) {
        & $pythonProject -X utf8 (Join-Path $PSScriptRoot $scriptName)
        if ($LASTEXITCODE -ne 0) { throw "Falha em $scriptName" }
    }
    & $nodeRuntime (Join-Path $PSScriptRoot 'exportar_excel.mjs')
    if ($LASTEXITCODE -ne 0) { throw 'Falha na exportação Excel.' }
    & $pythonRuntime -X utf8 (Join-Path $PSScriptRoot 'verificar_excel.py')
    if ($LASTEXITCODE -ne 0) { throw 'Falha na verificação final.' }
}
finally { Pop-Location }
