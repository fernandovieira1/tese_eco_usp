param([string]$ScriptPath = (Join-Path $PSScriptRoot '../chapters/chap1/stats/DASHBOARD/pt_h1/execucao_fe_candidatas/reproduzir_fe.ps1'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path -LiteralPath $ScriptPath).Path, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors) { throw ($parseErrors | Out-String) }
$call = $ast.Find({ param($node)
    $node -is [System.Management.Automation.Language.CommandAst] -and
    $node.Extent.Text -match 'extrair_candidatas\.py'
}, $true)
if (-not $call) { throw 'Etapa de extracao nao encontrada.' }
$stage = $call.Parent
if ($stage.Parent.Parent -is [System.Management.Automation.Language.IfStatementAst]) {
    $stage = $stage.Parent.Parent
}
# Executa so a etapa de selecao em pastas sinteticas; nenhum Python/Excel real e chamado.
$block = [scriptblock]::Create($stage.Extent.Text.Replace('$PSScriptRoot', '$candidateDirectory'))
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$testRoot = Join-Path $repoRoot ('2_INTI/audit/correcao_retomada_lotes_20261020/launcher_' + [guid]::NewGuid().ToString('N'))
$pythonRuntime = 'Invoke-FakeExtraction'
function Invoke-FakeExtraction {
    $script:extractions++
    Set-Content -LiteralPath $candidateFile -Value 'extraida' -Encoding ASCII
    $global:LASTEXITCODE = 0
}
foreach ($existing in @($true, $false)) {
    $candidateDirectory = Join-Path $testRoot ([string]$existing)
    New-Item -ItemType Directory -Path $candidateDirectory -Force | Out-Null
    $candidateFile = Join-Path $candidateDirectory 'candidatas_origem.json'
    if ($existing) { Set-Content -LiteralPath $candidateFile -Value 'original' -Encoding ASCII }
    $script:extractions = 0
    & $block
    if ($existing) {
        if ($script:extractions -ne 0 -or (Get-Content -LiteralPath $candidateFile -Raw).Trim() -ne 'original') {
            throw 'Retomada sobrescreveu a selecao de origem.'
        }
    } elseif ($script:extractions -ne 1 -or (Get-Content -LiteralPath $candidateFile -Raw).Trim() -ne 'extraida') {
        throw 'Lote novo nao extraiu a selecao de origem.'
    }
}
Write-Output 'OK: retomada preserva candidatas existentes; lote novo executa a extracao.'
