[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Snapshot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ===== CONFIGURACAO =====
$Source = $PSScriptRoot
$PermanentBackupDir = "D:\BACKUPS\Tese USP Fernando"
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

function Invoke-ResticSnapshotTarget {
    param(
        [Parameter(Mandatory=$true)][string]$TargetName,
        [Parameter(Mandatory=$true)][string]$RepoPath,
        [Parameter(Mandatory=$true)][string]$SourcePath,
        [Parameter(Mandatory=$true)][string]$PasswordPath,
        [Parameter(Mandatory=$true)][string]$ExcludeFile,
        [switch]$IsDryRun
    )

    if (-not (Test-Path -LiteralPath (Join-Path $RepoPath "config") -PathType Leaf)) {
        throw "Repositorio Restic nao inicializado em: $RepoPath"
    }

    $ResticArgs = @(
        "-r", $RepoPath,
        "--password-file", $PasswordPath,
        "backup", $SourcePath,
        "--exclude-file", $ExcludeFile,
        "--tag", "tese",
        "--tag", "manual"
    )

    if ($IsDryRun) {
        $ResticArgs += @("--dry-run", "--verbose")
        Write-Status "[BACKUP] DRY-RUN: simulando snapshot em $TargetName..."
    } else {
        Write-Status "[BACKUP] Executando snapshot em $TargetName..."
    }

    $resticExit = Invoke-NativeLogged -Command "restic" -Arguments $ResticArgs
    if ($resticExit -ne 0) {
        throw "Restic terminou com codigo $resticExit ao criar snapshot em $TargetName."
    }

    if (-not $IsDryRun) {
        Write-Status "[OK] Snapshot Restic criado com sucesso em $TargetName."

        Write-Status "Listando o snapshot mais recente em $TargetName..."
        $resticListExit = Invoke-NativeLogged -Command "restic" -Arguments @(
            "-r", $RepoPath,
            "--password-file", $PasswordPath,
            "snapshots", "--latest", "1"
        )
        if ($resticListExit -ne 0) {
            throw "O backup foi criado, mas falhou a verificacao da lista de snapshots em $TargetName."
        }
    }
}

# ===== PRE-CHECAGENS =====
if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "Origem nao encontrada: $Source"
}

$permanentDrive = [System.IO.Path]::GetPathRoot($PermanentBackupDir)
if (-not (Test-Path -LiteralPath $permanentDrive)) {
    throw "Unidade do destino permanente nao encontrada ou inacessivel: $permanentDrive"
}

# Deteccao dinamica do volume portatil pelo rotulo (FileSystemLabel)
$portableVolume = $null
$portableDriveRoot = $null
$BackupRoot = $null
$Mirror = $null
$GitDir = $null
$PortableResticRepo = $null
$LogsDir = $null

try {
    $foundVolumes = @(
        Get-Volume -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FileSystemLabel -eq $BackupLabel -and
            -not [string]::IsNullOrWhiteSpace($_.DriveLetter)
        }
    )

    if ($foundVolumes.Count -ge 1) {
        $candidateVolume = $foundVolumes[0]
        $candidateRoot = "$($candidateVolume.DriveLetter):\"
        if (Test-Path -LiteralPath $candidateRoot) {
            $portableVolume = $candidateVolume
            $portableDriveRoot = $candidateRoot
            $BackupRoot = Join-Path $portableDriveRoot "BACKUPS\dev_tese"
            $Mirror = Join-Path $BackupRoot "mirror"
            $GitDir = Join-Path $BackupRoot "git"
            $PortableResticRepo = Join-Path $BackupRoot "snapshots"
            $LogsDir = Join-Path $BackupRoot "logs"
        }
    }
}
catch {
    $portableVolume = $null
    $portableDriveRoot = $null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

if ($DryRun) {
    $script:RunLog = Join-Path $env:TEMP "backup_tese_DRYRUN_$timestamp.log"
} elseif ($portableVolume) {
    New-Item -ItemType Directory -Force $BackupRoot, $Mirror, $GitDir, $PortableResticRepo, $LogsDir | Out-Null
    $script:RunLog = Join-Path $LogsDir "backup_tese_$timestamp.log"
} else {
    $script:RunLog = Join-Path $env:TEMP "backup_tese_$timestamp.log"
}

New-Item -ItemType File -Force -Path $script:RunLog | Out-Null

if (-not $DryRun -and -not (Test-Path -LiteralPath $PermanentBackupDir)) {
    New-Item -ItemType Directory -Force -Path $PermanentBackupDir | Out-Null
}

Write-Status "Origem: $Source"
Write-Status "[OK] Destino principal disponivel: $PermanentBackupDir"

if ($portableVolume) {
    Write-Status "[OK] $BackupLabel detectado em $($portableVolume.DriveLetter): ($($portableVolume.FileSystem))"
    Write-Status ("Espaco livre no volume portatil: {0:N2} GiB" -f ($portableVolume.SizeRemaining / 1GB))
    if (($portableVolume.SizeRemaining / 1GB) -lt 5) {
        Write-Status "AVISO: menos de 5 GiB livres no disco portatil."
    } elseif (($portableVolume.SizeRemaining / 1GB) -lt 20) {
        Write-Status "AVISO: menos de 20 GiB livres no disco portatil."
    }
} else {
    Write-Status "[INFO] Volume $BackupLabel nao esta conectado. Backup portatil sera ignorado."
}

if ($DryRun) {
    Write-Status "MODO DRY-RUN: nenhuma copia persistente sera criada/alterada no disco de backup."
}

# ===== 1. GIT BUNDLE =====
$gitCheck = & git -C $Source rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $gitCheck -notcontains "true") {
    throw "A origem nao parece ser um repositorio Git valido."
}

if ($portableVolume) {
    try {
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
    }
    catch {
        $portableStepError = $_.Exception.Message
        Write-Status "[FALHA] Falha na sincronizacao do espelho/bundle em PORTATIL: $portableStepError"
        if (-not $Snapshot) {
            throw
        }
    }
}

# ===== 3. SNAPSHOT RESTIC OPCIONAL =====
if ($Snapshot) {
    if (-not (Get-Command restic -ErrorAction SilentlyContinue)) {
        throw "Restic nao encontrado no PATH."
    }

    if (-not (Test-Path -LiteralPath $PasswordFile -PathType Leaf)) {
        throw "Arquivo de senha do Restic nao encontrado: $PasswordFile"
    }

    $backupTargets = @()

    # Destino permanente (obrigatorio)
    $backupTargets += [PSCustomObject]@{
        Id          = "Permanent"
        Name        = "D"
        Path        = $PermanentBackupDir
        IsMandatory = $true
    }

    # Destino portatil (opcional)
    if ($portableVolume) {
        $backupTargets += [PSCustomObject]@{
            Id          = "Portable"
            Name        = "PORTATIL ($($portableVolume.DriveLetter):)"
            Path        = $PortableResticRepo
            IsMandatory = $false
        }
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

    $targetResults = @{}

    try {
        foreach ($target in $backupTargets) {
            try {
                Invoke-ResticSnapshotTarget -TargetName $target.Name `
                                            -RepoPath $target.Path `
                                            -SourcePath $Source `
                                            -PasswordPath $PasswordFile `
                                            -ExcludeFile $ResticExcludeFile `
                                            -IsDryRun:$DryRun
                $targetResults[$target.Id] = @{
                    Target  = $target
                    Success = $true
                    Message = "Concluido com sucesso."
                }
                Write-Status "[OK] Backup $($target.Name) concluido."
            }
            catch {
                $err = $_.Exception.Message
                $targetResults[$target.Id] = @{
                    Target  = $target
                    Success = $false
                    Message = $err
                }
                Write-Status "[FALHA] Falha no backup em $($target.Name): $err"
            }
        }
    }
    finally {
        if (Test-Path -LiteralPath $ResticExcludeFile) {
            Remove-Item -LiteralPath $ResticExcludeFile -Force
        }
    }

    # Validacao dos resultados
    $permanentResult = $targetResults["Permanent"]
    if (-not $permanentResult.Success) {
        throw "Falha no destino permanente obrigatorio ($($permanentResult.Target.Path)): $($permanentResult.Message)"
    }

    if ($targetResults.ContainsKey("Portable")) {
        $portableResult = $targetResults["Portable"]
        if (-not $portableResult.Success) {
            Write-Status "[AVISO] O destino portatil falhou, mas o destino principal (D:) foi concluido com sucesso."
        }
    }
}

# ===== FINAL =====
if ($DryRun) {
    Write-Status "DRY-RUN concluido. Log temporario: $($script:RunLog)"
} else {
    if ($portableVolume) {
        $volumeFinal = Get-Volume -DriveLetter $portableVolume.DriveLetter -ErrorAction SilentlyContinue
        if ($volumeFinal) {
            Write-Status ("Espaco livre restante em $($portableVolume.DriveLetter):: {0:N2} GiB" -f ($volumeFinal.SizeRemaining / 1GB))
        }
    }
    Write-Status "Backup concluido."
    Write-Status "Log: $($script:RunLog)"
}
