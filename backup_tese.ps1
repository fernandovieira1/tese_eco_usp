<#
.SYNOPSIS
    Backup da tese: snapshot Restic (D: e PORTATIL), Git bundle e espelho Robocopy (PORTATIL).
.DESCRIPTION
    Por padrao, cria snapshot Restic no destino permanente (D:, obrigatorio). Se o volume
    PORTATIL estiver conectado, tambem atualiza o Git bundle, o espelho Robocopy e o
    snapshot Restic no PORTATIL. A cada $CheckIntervalDays dias (ou com -Check), executa
    "restic check --read-data-subset" em cada repositorio que recebeu o snapshot.
.PARAMETER DryRun
    Simula as operacoes sem gravar no disco de backup.
.PARAMETER SkipSnapshot
    Nao executa o Restic (somente Git bundle + espelho no PORTATIL).
.PARAMETER Check
    Forca a verificacao "restic check", independentemente do intervalo configurado.
.PARAMETER Snapshot
    Obsoleto: o snapshot Restic agora e padrao. Mantido apenas por compatibilidade.
.NOTES
    Codigos de saida: 0 = sucesso (com ou sem avisos); 1 = uma ou mais etapas falharam.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipSnapshot,
    [switch]$Check,
    [switch]$Snapshot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ===== CONFIGURACAO =====
$Source = $PSScriptRoot
$PermanentBackupDir = "D:\BACKUPS\Tese USP Fernando"
$BackupLabel = "PORTATIL"
$PasswordFile = "$env:USERPROFILE\.restic\tese-backup-password.txt"

# Verificacao periodica de integridade dos repositorios Restic
$CheckIntervalDays = 30
$CheckReadDataSubset = "10%"
$CheckStateDir = "$env:USERPROFILE\.restic"

# Lista unica de exclusoes: usada pelo Robocopy (/XD e /XF) e pelo Restic (--exclude-file)
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

# Resultados de cada etapa, apresentados no resumo final
$script:Results = New-Object System.Collections.Generic.List[object]

function Write-Status {
    param(
        [string]$Message,
        [string]$Color = ""
    )
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    if ($Color) {
        Write-Host "[$stamp] $Message" -ForegroundColor $Color
    } else {
        Write-Host "[$stamp] $Message"
    }
    if ($script:RunLog) {
        Add-Content -LiteralPath $script:RunLog -Value "[$stamp] $Message" -Encoding UTF8
    }
}

function Add-Result {
    param(
        [Parameter(Mandatory=$true)][ValidateSet("OK", "AVISO", "FALHA")][string]$Status,
        [Parameter(Mandatory=$true)][string]$Step,
        [Parameter(Mandatory=$true)][string]$Message
    )
    $script:Results.Add([PSCustomObject]@{
        Status  = $Status
        Step    = $Step
        Message = $Message
    })
    $color = switch ($Status) { "OK" { "Green" } "AVISO" { "Yellow" } default { "Red" } }
    Write-Status "[$Status] ${Step}: $Message" -Color $color
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

function Get-ResticVersion {
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $text = (& restic version 2>&1 | Out-String)
    }
    finally {
        $ErrorActionPreference = $oldEAP
    }
    if ($text -match 'restic (\d+)\.(\d+)\.(\d+)') {
        return [version]("{0}.{1}.{2}" -f $Matches[1], $Matches[2], $Matches[3])
    }
    return $null
}

function Get-LastCheckDate {
    param([Parameter(Mandatory=$true)][string]$StatePath)

    if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) { return $null }
    $raw = Get-Content -LiteralPath $StatePath -TotalCount 1
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }

    $parsed = [datetime]::MinValue
    $ok = [datetime]::TryParseExact(
        $raw.Trim(), "yyyy-MM-dd HH:mm:ss",
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::None,
        [ref]$parsed
    )
    if ($ok) { return $parsed }
    return $null
}

function Invoke-ResticSnapshotTarget {
    param(
        [Parameter(Mandatory=$true)][string]$TargetName,
        [Parameter(Mandatory=$true)][string]$RepoPath,
        [Parameter(Mandatory=$true)][string]$SourcePath,
        [Parameter(Mandatory=$true)][string]$PasswordPath,
        [Parameter(Mandatory=$true)][string]$ExcludeFile,
        [string[]]$ExtraArgs = @(),
        [switch]$IsDryRun
    )

    # Retorna @{ Status = "OK" | "AVISO"; Message = ... } ou lanca excecao em caso de falha.

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
    ) + $ExtraArgs

    if ($IsDryRun) {
        $ResticArgs += @("--dry-run", "--verbose")
        Write-Status "[BACKUP] DRY-RUN: simulando snapshot em $TargetName..."
    } else {
        Write-Status "[BACKUP] Executando snapshot em $TargetName..."
    }

    $resticExit = Invoke-NativeLogged -Command "restic" -Arguments $ResticArgs

    # Restic: 0 = sucesso; 3 = snapshot criado, mas alguns arquivos nao puderam ser lidos.
    $status = "OK"
    $message = if ($IsDryRun) { "Simulacao concluida." } else { "Snapshot concluido." }
    if ($resticExit -eq 3) {
        $status = "AVISO"
        $message = "Snapshot criado, mas alguns arquivos nao puderam ser lidos (codigo 3). Consulte o log."
    } elseif ($resticExit -ne 0) {
        throw "Restic terminou com codigo $resticExit ao criar snapshot em $TargetName."
    }

    if (-not $IsDryRun) {
        # Apenas informativo: a verificacao de integridade e feita por "restic check".
        Write-Status "Snapshot mais recente em ${TargetName}:"
        $resticListExit = Invoke-NativeLogged -Command "restic" -Arguments @(
            "-r", $RepoPath,
            "--password-file", $PasswordPath,
            "snapshots", "--latest", "1"
        )
        if ($resticListExit -ne 0) {
            $status = "AVISO"
            $message += " Falhou a listagem do snapshot mais recente (codigo $resticListExit)."
        }
    }

    return @{ Status = $status; Message = $message }
}

# ===== PRE-CHECAGENS =====
if ($Snapshot -and $SkipSnapshot) {
    throw "Parametros conflitantes: -Snapshot e -SkipSnapshot."
}
if ($Check -and $SkipSnapshot) {
    throw "Parametros conflitantes: -Check exige o Restic e nao pode ser usado com -SkipSnapshot."
}
$RunSnapshot = -not $SkipSnapshot

if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "Origem nao encontrada: $Source"
}

if ($RunSnapshot) {
    $permanentDrive = [System.IO.Path]::GetPathRoot($PermanentBackupDir)
    if (-not (Test-Path -LiteralPath $permanentDrive)) {
        throw "Unidade do destino permanente nao encontrada ou inacessivel: $permanentDrive"
    }
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

if (-not $RunSnapshot -and -not $portableVolume) {
    throw "Nada a fazer: -SkipSnapshot foi usado e o volume $BackupLabel nao esta conectado."
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

# Log proprio do Robocopy, separado do log UTF-8. "/UNILOG:" (sem "+") grava UTF-16 com BOM,
# preservando acentos; "/UNILOG+" grava na pagina de codigo OEM. O nome e unico por execucao.
$RoboLog = [System.IO.Path]::ChangeExtension($script:RunLog, $null).TrimEnd(".") + "_robocopy.log"

New-Item -ItemType File -Force -Path $script:RunLog | Out-Null

if ($RunSnapshot -and -not $DryRun -and -not (Test-Path -LiteralPath $PermanentBackupDir)) {
    New-Item -ItemType Directory -Force -Path $PermanentBackupDir | Out-Null
}

Write-Status "Origem: $Source"

if ($Snapshot) {
    Write-Status "[INFO] -Snapshot e obsoleto: o snapshot Restic agora e executado por padrao."
}

if ($RunSnapshot) {
    Write-Status "[OK] Destino principal (Restic) disponivel: $PermanentBackupDir"
} else {
    Write-Status "[INFO] -SkipSnapshot: Restic desativado; o destino principal ($PermanentBackupDir) nao sera atualizado."
}

if ($portableVolume) {
    Write-Status "[OK] $BackupLabel detectado em $($portableVolume.DriveLetter): ($($portableVolume.FileSystem))"
    Write-Status ("Espaco livre no volume portatil: {0:N2} GiB" -f ($portableVolume.SizeRemaining / 1GB))
    if (($portableVolume.SizeRemaining / 1GB) -lt 5) {
        Write-Status "AVISO: menos de 5 GiB livres no disco portatil." -Color "Yellow"
    } elseif (($portableVolume.SizeRemaining / 1GB) -lt 20) {
        Write-Status "AVISO: menos de 20 GiB livres no disco portatil." -Color "Yellow"
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

            Add-Result -Status "OK" -Step "Git bundle ($BackupLabel)" -Message (
                "Atualizado: {0:N2} MiB" -f ((Get-Item -LiteralPath $BundleDest).Length / 1MB)
            )
        }
    }
    catch {
        Add-Result -Status "FALHA" -Step "Git bundle ($BackupLabel)" -Message $_.Exception.Message
    }

    # ===== 2. ESPELHO INCREMENTAL NAO-DESTRUTIVO =====
    # /E        = copia subpastas, inclusive vazias
    # /FFT      = tolerancia de timestamp adequada a exFAT/FAT
    # /COPY:DAT = dados, atributos e timestamps (sem ACL NTFS)
    # /DCOPY:DAT= equivalente para diretorios
    # /XJ       = evita seguir junctions
    # Nao usamos /MIR nem /PURGE: exclusoes na origem nao sao propagadas automaticamente.
    try {
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
            "/UNILOG:$RoboLog",
            "/XD"
        ) + $ExcludedDirs + @("/XF") + $ExcludedFiles

        if ($DryRun) {
            $RoboArgs += "/L"
        }

        Write-Status "Executando copia incremental com Robocopy (log: $RoboLog)..."
        & robocopy @RoboArgs
        $roboExit = $LASTEXITCODE

        # Robocopy: 0-7 = sucesso/variacoes benignas; >=8 = falha.
        if ($roboExit -ge 8) {
            throw "Robocopy terminou com codigo $roboExit (falha). Consulte o log: $RoboLog"
        }
        Add-Result -Status "OK" -Step "Espelho Robocopy ($BackupLabel)" -Message "Concluido com codigo $roboExit."
    }
    catch {
        Add-Result -Status "FALHA" -Step "Espelho Robocopy ($BackupLabel)" -Message $_.Exception.Message
    }
}

# ===== 3. SNAPSHOT RESTIC (PADRAO) + VERIFICACAO PERIODICA =====
if ($RunSnapshot) {
    if (-not (Get-Command restic -ErrorAction SilentlyContinue)) {
        throw "Restic nao encontrado no PATH."
    }

    if (-not (Test-Path -LiteralPath $PasswordFile -PathType Leaf)) {
        throw "Arquivo de senha do Restic nao encontrado: $PasswordFile"
    }

    $ExtraBackupArgs = @()

    # --skip-if-unchanged (restic >= 0.17): nao cria snapshot quando nada mudou.
    $resticVersion = Get-ResticVersion
    if ($resticVersion -and $resticVersion -ge [version]"0.17.0") {
        $ExtraBackupArgs += "--skip-if-unchanged"
    } else {
        Write-Status "[INFO] Versao do restic anterior a 0.17 ou desconhecida: --skip-if-unchanged nao sera usado."
    }

    # --use-fs-snapshot (VSS) exige privilegios de administrador.
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
    if ($isAdmin -and -not $DryRun) {
        $ExtraBackupArgs += "--use-fs-snapshot"
        Write-Status "[INFO] Executando como administrador: snapshot com VSS (--use-fs-snapshot)."
    } elseif (-not $isAdmin) {
        Write-Status "[INFO] Sem privilegios de administrador: snapshot sem VSS. Feche arquivos em edicao antes do backup."
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
    # ASCII: evita BOM; todos os padroes sao ASCII.
    ($ExcludedDirs + $ExcludedFiles) | Set-Content -LiteralPath $ResticExcludeFile -Encoding ASCII

    try {
        foreach ($target in $backupTargets) {
            $mandatoryTag = if ($target.IsMandatory) { ", obrigatorio" } else { "" }
            $stepName = "Restic $($target.Name)$mandatoryTag"
            $backupOk = $false

            try {
                $r = Invoke-ResticSnapshotTarget -TargetName $target.Name `
                                                 -RepoPath $target.Path `
                                                 -SourcePath $Source `
                                                 -PasswordPath $PasswordFile `
                                                 -ExcludeFile $ResticExcludeFile `
                                                 -ExtraArgs $ExtraBackupArgs `
                                                 -IsDryRun:$DryRun
                Add-Result -Status $r.Status -Step $stepName -Message $r.Message
                $backupOk = $true
            }
            catch {
                Add-Result -Status "FALHA" -Step $stepName -Message $_.Exception.Message
            }

            if (-not $backupOk) { continue }

            # ----- Verificacao periodica de integridade (restic check) -----
            $checkStep = "Check $($target.Name)"
            $statePath = Join-Path $CheckStateDir "tese-last-check-$($target.Id).txt"
            $lastCheck = Get-LastCheckDate -StatePath $statePath
            $isDue = $Check -or (-not $lastCheck) -or (((Get-Date) - $lastCheck).TotalDays -ge $CheckIntervalDays)

            if (-not $isDue) {
                $daysLeft = [math]::Ceiling($CheckIntervalDays - ((Get-Date) - $lastCheck).TotalDays)
                Write-Status ("[INFO] {0}: ultimo restic check em {1:yyyy-MM-dd}; proximo em ~{2} dia(s)." -f $checkStep, $lastCheck, $daysLeft)
                continue
            }

            if ($DryRun) {
                Write-Status "DRY-RUN: restic check --read-data-subset=$CheckReadDataSubset seria executado em $($target.Name)."
                continue
            }

            Write-Status "[CHECK] Verificando integridade em $($target.Name) (restic check --read-data-subset=$CheckReadDataSubset)..."
            $checkExit = Invoke-NativeLogged -Command "restic" -Arguments @(
                "-r", $target.Path,
                "--password-file", $PasswordFile,
                "check", "--read-data-subset=$CheckReadDataSubset"
            )

            if ($checkExit -eq 0) {
                Set-Content -LiteralPath $statePath -Value (Get-Date -Format "yyyy-MM-dd HH:mm:ss") -Encoding ASCII
                Add-Result -Status "OK" -Step $checkStep -Message "Integridade verificada (amostra de $CheckReadDataSubset dos dados)."
            } else {
                Add-Result -Status "FALHA" -Step $checkStep -Message "restic check terminou com codigo $checkExit. Investigue o repositorio antes do proximo backup."
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
if (-not $DryRun -and $portableVolume) {
    $volumeFinal = Get-Volume -DriveLetter $portableVolume.DriveLetter -ErrorAction SilentlyContinue
    if ($volumeFinal) {
        Write-Status ("Espaco livre restante em $($portableVolume.DriveLetter):: {0:N2} GiB" -f ($volumeFinal.SizeRemaining / 1GB))
    }
}

$failures = @($script:Results | Where-Object { $_.Status -eq "FALHA" })
$warnings = @($script:Results | Where-Object { $_.Status -eq "AVISO" })

Write-Status "===== RESUMO ====="
foreach ($item in $script:Results) {
    $color = switch ($item.Status) { "OK" { "Green" } "AVISO" { "Yellow" } default { "Red" } }
    Write-Status ("[{0}] {1}: {2}" -f $item.Status, $item.Step, $item.Message) -Color $color
}

$prefix = if ($DryRun) { "DRY-RUN concluido" } else { "Backup concluido" }
Write-Status "Log: $($script:RunLog)"
if ($portableVolume) {
    Write-Status "Log do Robocopy: $RoboLog"
}

if ($failures.Count -gt 0) {
    Write-Status ("{0} COM {1} FALHA(S). Revise o resumo acima." -f $prefix, $failures.Count) -Color "Red"
    exit 1
}
if ($warnings.Count -gt 0) {
    Write-Status ("{0} com {1} aviso(s)." -f $prefix, $warnings.Count) -Color "Yellow"
} else {
    Write-Status "$prefix com sucesso." -Color "Green"
}
exit 0
