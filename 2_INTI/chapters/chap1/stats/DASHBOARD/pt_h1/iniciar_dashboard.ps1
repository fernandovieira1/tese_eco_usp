param(
    [ValidateRange(1024, 65535)][int]$Port = 8503,
    [switch]$Foreground
)
$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
while (-not (Test-Path -LiteralPath (Join-Path $repoRoot '2_INTI/RESEARCH_PROTOCOL.md'))) {
    $parentDirectory = Split-Path -Parent $repoRoot
    if (-not $parentDirectory -or $parentDirectory -eq $repoRoot) { throw 'Raiz do repositório não encontrada.' }
    $repoRoot = $parentDirectory
}
$pythonPath = Join-Path $repoRoot '.venv/Scripts/python.exe'
$appPath = Join-Path $PSScriptRoot 'app.py'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Ambiente .venv da raiz não encontrado. Consulte README.md.' }
$listening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listening) { throw "A porta $Port já está em uso. Confira o servidor existente ou escolha -Port 8504." }
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$arguments = @('-X', 'utf8', '-m', 'streamlit', 'run', $appPath,
    '--server.address=127.0.0.1', "--server.port=$Port", '--server.headless=true',
    '--browser.gatherUsageStats=false', '--theme.base=light', '--theme.primaryColor=#13796b')
if ($Foreground) {
    Push-Location $PSScriptRoot
    try { & $pythonPath @arguments }
    finally { Pop-Location }
} else {
    $logDirectory = Join-Path $repoRoot '2_INTI/audit/dashboard_h1_runtime'
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $outLog = Join-Path $logDirectory "streamlit_${Port}_${stamp}.stdout.log"
    $errLog = Join-Path $logDirectory "streamlit_${Port}_${stamp}.stderr.log"
    # Start-Process joins arguments into a command line; quote the path containing spaces.
    $arguments[5] = '"' + $appPath + '"'
    $process = Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $PSScriptRoot `
        -WindowStyle Hidden -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru
    Write-Output "Dashboard iniciado (PID $($process.Id)): http://127.0.0.1:$Port"
    Write-Output "Logs: $logDirectory"
}
