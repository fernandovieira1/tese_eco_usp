# Testa as exclusoes reais sem executar o backup dos discos do usuario.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    (Join-Path $repoRoot 'backup_tese.ps1'), [ref]$tokens, [ref]$parseErrors)
if ($parseErrors) { throw ($parseErrors | Out-String) }

# Avalia somente as listas e o comando que grava as exclusoes, nunca o script inteiro.
foreach ($name in @('ExcludedDirs', 'ExcludedFiles')) {
    $assignment = $ast.Find({ param($node)
        $node -is [System.Management.Automation.Language.AssignmentStatementAst] -and
        $node.Left -is [System.Management.Automation.Language.VariableExpressionAst] -and
        $node.Left.VariablePath.UserPath -eq $name
    }, $true)
    if (-not $assignment) { throw "Lista nao encontrada: $name" }
    . ([scriptblock]::Create($assignment.Extent.Text))
}
$pipeline = $ast.Find({ param($node)
    $node -is [System.Management.Automation.Language.PipelineAst] -and
    $node.Extent.Text -match '\$ExcludedDirs\s*\+\s*\$ExcludedFiles' -and
    $node.Extent.Text -match 'Set-Content'
}, $true)
if (-not $pipeline) { throw 'Gravacao das exclusoes Restic nao encontrada.' }
$auditRoot = Join-Path $repoRoot '2_INTI/audit/correcao_backup_git_20261020'
$workDir = Join-Path $auditRoot ('teste_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $workDir -Force | Out-Null
$ResticExcludeFile = Join-Path $workDir 'excludes.txt'
& ([scriptblock]::Create($pipeline.Extent.Text))
$resticExclusions = @(Get-Content -LiteralPath $ResticExcludeFile)
if ($resticExclusions -contains '.git') { throw 'Restic ainda exclui o historico Git.' }
if ($ExcludedDirs -notcontains '.git') { throw 'Robocopy deixou de excluir .git.' }
$expectedExclusions = @($ExcludedDirs + $ExcludedFiles | Where-Object { $_ -ne '.git' })
if (Compare-Object $expectedExclusions $resticExclusions) { throw 'Outra exclusao foi alterada.' }

$source = Join-Path $workDir 'source'
$files = @('.git/HEAD', '.git/refs/heads/main', '.git/objects/ab/objeto', 'texto.txt')
foreach ($relative in @($files) + @('.venv/ignorado.txt', 'descartavel.pyc')) {
    $path = Join-Path $source $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
    Set-Content -LiteralPath $path -Value "fixture: $relative" -Encoding ASCII
}
$password = Join-Path $workDir 'senha_teste.txt'
[guid]::NewGuid().ToString() | Set-Content -LiteralPath $password -Encoding ASCII
$resticRepo = Join-Path $workDir 'restic_repo'
$restore = Join-Path $workDir 'restore'
$resticArgs = @('-r', $resticRepo, '--password-file', $password, '--no-cache', '--quiet')
& restic @resticArgs init
if ($LASTEXITCODE -ne 0) { throw 'Falha ao inicializar Restic de teste.' }
& restic @resticArgs backup $source --exclude-file $ResticExcludeFile
if ($LASTEXITCODE -ne 0) { throw 'Falha no snapshot de teste.' }
$subtree = 'latest:/' + $source.Replace('\', '/').Replace(':', '')
& restic @resticArgs restore $subtree --target $restore
if ($LASTEXITCODE -ne 0) { throw 'Falha na restauracao de teste.' }
foreach ($relative in $files) {
    $original = (Get-FileHash -LiteralPath (Join-Path $source $relative) -Algorithm SHA256).Hash
    $restored = (Get-FileHash -LiteralPath (Join-Path $restore $relative) -Algorithm SHA256).Hash
    if ($original -ne $restored) { throw "Conteudo restaurado divergente: $relative" }
}
foreach ($relative in @('.venv', 'descartavel.pyc')) {
    if (Test-Path -LiteralPath (Join-Path $restore $relative)) {
        throw "Exclusao Restic nao respeitada: $relative"
    }
}
$mirror = Join-Path $workDir 'mirror'
$roboArgs = @($source, $mirror, '/E', '/XJ', '/R:0', '/W:0', '/NFL', '/NDL', '/NJH', '/NJS', '/NP', '/XD') +
    $ExcludedDirs + @('/XF') + $ExcludedFiles
& robocopy @roboArgs
if ($LASTEXITCODE -ge 8) { throw 'Falha no espelho de teste.' }
if (Test-Path -LiteralPath (Join-Path $mirror '.git')) { throw 'Robocopy copiou .git.' }
if (-not (Test-Path -LiteralPath (Join-Path $mirror 'texto.txt'))) { throw 'Espelho nao copiou o arquivo comum.' }
Write-Output 'OK: .git restaurado com hashes identicos; demais exclusoes preservadas; Robocopy omite .git.'
Write-Output "Artefatos: $workDir"
exit 0
