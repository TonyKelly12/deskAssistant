#Requires -Version 5.1
<#
  Push pi/bot_brain to the Pi from Windows (no rsync required).
  Uses tar over SSH — one stream, works with OpenSSH bundled in Windows 10+.

  Usage (PowerShell):
    $env:PI = "pi@192.168.1.42"
    .\pi\sync_to_pi.ps1

  For incremental syncs like rsync, use WSL:  wsl bash pi/sync_to_pi.sh
  Or use git pull on the Pi (see pi/DEV_SYNC.txt).
#>
param(
    [string] $Pi = $env:PI
)
if (-not $Pi) {
    $Pi = "pi@raspberrypi.local"
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src = Join-Path $ScriptDir "bot_brain"
if (-not (Test-Path -LiteralPath $Src)) {
    Write-Error "Missing folder: $Src"
    exit 1
}

# Mirror remote bot_brain to match local (removes stale files on Pi)
ssh $Pi "rm -rf ~/bot_brain && mkdir -p ~/bot_brain"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Stream archive (POSIX tar from Windows tar.exe)
Push-Location $Src
try {
    tar -cf - --exclude='__pycache__' --exclude='*.pyc' . | ssh $Pi "tar -xf - -C ~/bot_brain"
} finally {
    Pop-Location
}

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Synced to ${Pi}:~/bot_brain/"
