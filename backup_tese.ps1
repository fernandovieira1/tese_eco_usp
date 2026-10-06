[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Snapshot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ===== CONFIGURACAO =====
$Source = "C:\Users\ferna\Documents\dev\Tese USP\tese_eco_usp"
$BackupLabel = "PORTATIL"
$PasswordFile = "$env:USERPROFILE\.restic\tese-backup-password.txt"

$ExcludedDirs = @(
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "node_modules",
    "build",
    "dist",
    ".tox",
    ".cache",
    "htmlcov"
)

$ExcludedFiles = @(
    "*.pyc",
    "*.pyo",
    "*.tmp",
    "*.temp",
    "~$*",
    ".DS_Store",
    "Thumbs.db"
)

function Write-Status {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$stamp] $Message"
    if ($script:RunLog) {
        Add-Content -LiteralPath $script:RunLog -Value "[$stamp] $Message" -Encoding UTF8
    }
}

function Invoke-NativeLogged {
    param(
        [Parameter(Mandatory=$true)][string]$Command,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    # Windows PowerShell 5.1 pode transformar texto escrito em STDERR por
    # programas nativos em NativeCommandError quando 2>&1 e
    # ErrorActionPreference=Stop. Git e Restic usam STDERR inclusive para
    # mensagens informativas. Aqui exibimos e registramos essas mensagens,
    # mas consideramos sucesso/falha exclusivamente pelo exit code nativo.
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Command @Arguments 2>&1 | ForEach-Object {
            $line = $_.ToString()
            Write-Host $line
            Add-Content -LiteralPath $script:RunLog -Value $line -Encoding UTF8
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldEAP
    }

    return [int]$exitCode
}

# ===== PRE-CHECAGENS =====
if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "Origem nao encontrada: $Source"
}

$volumes = @(
    Get-Volume |
    Where-Object {
        $_.FileSystemLabel -eq $BackupLabel -and
        $_.FileSystem -eq "exFAT" -and
        $null -ne $_.DriveLetter
    }
)

if ($volumes.Count -ne 1) {
    throw "Esperava encontrar exatamente um volume exFAT com rotulo '$BackupLabel'. Encontrados: $($volumes.Count)."
}

$volume = $volumes[0]
$DriveRoot = "$($volume.DriveLetter):\"
$BackupRoot = Join-Path $DriveRoot "BACKUPS\dev_tese"
$Mirror = Join-Path $BackupRoot "mirror"
$GitDir = Join-Path $BackupRoot "git"
$ResticRepo = Join-Path $BackupRoot "snapshots"
$LogsDir = Join-Path $BackupRoot "logs"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

if ($DryRun) {
    $script:RunLog = Join-Path $env:TEMP "backup_tese_DRYRUN_$timestamp.log"
} else {
    New-Item -ItemType Directory -Force $BackupRoot, $Mirror, $GitDir, $ResticRepo, $LogsDir | Out-Null
    $script:RunLog = Join-Path $LogsDir "backup_tese_$timestamp.log"
}

New-Item -ItemType File -Force -Path $script:RunLog | Out-Null

Write-Status "Origem: $Source"
Write-Status "Destino detectado: $DriveRoot ($BackupLabel / exFAT)"
Write-Status ("Espaco livre: {0:N2} GiB" -f ($volume.SizeRemaining / 1GB))
if ($DryRun) {
    Write-Status "MODO DRY-RUN: nenhuma copia persistente sera criada/alterada no disco de backup."
}

if (($volume.SizeRemaining / 1GB) -lt 5) {
    throw "Menos de 5 GiB livres no disco de backup. Operacao abortada."
} elseif (($volume.SizeRemaining / 1GB) -lt 20) {
    Write-Status "AVISO: menos de 20 GiB livres no disco de backup."
}

# ===== 1. GIT BUNDLE =====
$gitCheck = & git -C $Source rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $gitCheck -notcontains "true") {
    throw "A origem nao parece ser um repositorio Git valido."
}

$BundleDest = Join-Path $GitDir "tese_eco_usp.bundle"
$BundlePrev = Join-Path $GitDir "tese_eco_usp.previous.bundle"
$BundleNew = Join-Path $GitDir "tese_eco_usp.bundle.new"
$TempBundle = Join-Path $env:TEMP "tese_eco_usp_$timestamp.bundle"

if ($DryRun) {
    Write-Status "DRY-RUN: Git bundle seria recriado em $BundleDest"
} else {
    Write-Status "Criando Git bundle..."
    if (Test-Path -LiteralPath $TempBundle) { Remove-Item -LiteralPath $TempBundle -Force }

    $gitCreateExit = Invoke-NativeLogged -Command "git" -Arguments @(
        "-C", $Source, "bundle", "create", $TempBundle, "--all"
    )
    if ($gitCreateExit -ne 0) {
        throw "Falha ao criar Git bundle (codigo $gitCreateExit)."
    }

    $gitVerifyExit = Invoke-NativeLogged -Command "git" -Arguments @(
        "-C", $Source, "bundle", "verify", $TempBundle
    )
    if ($gitVerifyExit -ne 0) {
        throw "Falha na verificacao do Git bundle (codigo $gitVerifyExit)."
    }

    Copy-Item -LiteralPath $TempBundle -Destination $BundleNew -Force

    $hashTemp = (Get-FileHash -LiteralPath $TempBundle -Algorithm SHA256).Hash
    $hashNew  = (Get-FileHash -LiteralPath $BundleNew -Algorithm SHA256).Hash
    if ($hashTemp -ne $hashNew) {
        throw "Falha de integridade ao copiar o Git bundle para o disco de backup."
    }

    if (Test-Path -LiteralPath $BundlePrev) {
        Remove-Item -LiteralPath $BundlePrev -Force
    }
    if (Test-Path -LiteralPath $BundleDest) {
        Move-Item -LiteralPath $BundleDest -Destination $BundlePrev
    }
    Move-Item -LiteralPath $BundleNew -Destination $BundleDest
    Remove-Item -LiteralPath $TempBundle -Force

    Write-Status ("Git bundle atualizado: {0:N2} MiB" -f ((Get-Item -LiteralPath $BundleDest).Length / 1MB))
}

# ===== 2. ESPELHO INCREMENTAL NAO-DESTRUTIVO =====
# /E        = copia subpastas, inclusive vazias
# /FFT      = tolerancia de timestamp adequada a exFAT/FAT
# /COPY:DAT = dados, atributos e timestamps (sem ACL NTFS)
# /DCOPY:DAT= equivalente para diretorios
# /XJ       = evita seguir junctions
# Nao usamos /MIR nem /PURGE: exclusoes na origem nao sao propagadas automaticamente.

$RoboArgs = @(
    $Source,
    $Mirror,
    "/E",
    "/Z",
    "/FFT",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/R:2",
    "/W:2",
    "/XJ",
    "/NP",
    "/TEE",
    "/UNILOG+:$($script:RunLog)",
    "/XD"
) + $ExcludedDirs + @("/XF") + $ExcludedFiles

if ($DryRun) {
    $RoboArgs += "/L"
}

Write-Status "Executando copia incremental com Robocopy..."
& robocopy @RoboArgs
$roboExit = $LASTEXITCODE

# Robocopy: 0-7 = sucesso/variacoes benignas; >=8 = falha.
if ($roboExit -ge 8) {
    throw "Robocopy terminou com codigo $roboExit (falha). Consulte o log: $($script:RunLog)"
}
Write-Status "Robocopy concluido com codigo $roboExit."

# ===== 3. SNAPSHOT RESTIC OPCIONAL =====
if ($Snapshot) {
    if (-not (Get-Command restic -ErrorAction SilentlyContinue)) {
        throw "Restic nao encontrado no PATH."
    }

    if (-not (Test-Path -LiteralPath $PasswordFile -PathType Leaf)) {
        throw "Arquivo de senha do Restic nao encontrado: $PasswordFile"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $ResticRepo "config") -PathType Leaf)) {
        throw "Repositorio Restic nao inicializado em: $ResticRepo"
    }

    $ResticExcludeFile = Join-Path $env:TEMP "restic_excludes_tese_$timestamp.txt"
    @(
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".ipynb_checkpoints",
        "node_modules",
        "build",
        "dist",
        ".tox",
        ".cache",
        "htmlcov",
        "*.pyc",
        "*.pyo",
        "*.tmp",
        "*.temp",
        "~$*",
        ".DS_Store",
        "Thumbs.db"
    ) | Set-Content -LiteralPath $ResticExcludeFile -Encoding UTF8

    try {
        $ResticArgs = @(
            "-r", $ResticRepo,
            "--password-file", $PasswordFile,
            "backup", $Source,
            "--exclude-file", $ResticExcludeFile,
            "--tag", "tese",
            "--tag", "manual"
        )

        if ($DryRun) {
            $ResticArgs += @("--dry-run", "--verbose")
            Write-Status "DRY-RUN: simulando snapshot Restic..."
        } else {
            Write-Status "Criando snapshot Restic..."
        }

        $resticExit = Invoke-NativeLogged -Command "restic" -Arguments $ResticArgs
        if ($resticExit -ne 0) {
            throw "Restic terminou com codigo $resticExit."
        }

        if (-not $DryRun) {
            Write-Status "Snapshot Restic criado com sucesso."

            Write-Status "Listando o snapshot mais recente..."
            $resticListExit = Invoke-NativeLogged -Command "restic" -Arguments @(
                "-r", $ResticRepo,
                "--password-file", $PasswordFile,
                "snapshots", "--latest", "1"
            )
            if ($resticListExit -ne 0) {
                throw "O backup foi criado, mas falhou a verificacao da lista de snapshots."
            }
        }
    }
    finally {
        if (Test-Path -LiteralPath $ResticExcludeFile) {
            Remove-Item -LiteralPath $ResticExcludeFile -Force
        }
    }
}

# ===== FINAL =====
if ($DryRun) {
    Write-Status "DRY-RUN concluido. Log temporario: $($script:RunLog)"
} else {
    $volumeFinal = Get-Volume -DriveLetter $volume.DriveLetter
    Write-Status ("Backup concluido. Espaco livre restante: {0:N2} GiB" -f ($volumeFinal.SizeRemaining / 1GB))
    Write-Status "Log: $($script:RunLog)"
}
