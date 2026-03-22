# Build DeskAssistant natively (for dev or when building ON the target device)
# Requires: CMake, libmosquitto-dev (on Linux)
param([string]$Target = "native")

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$BuildDir = Join-Path $ProjectRoot "build"

Write-Host "Building for $Target (native)..."
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
Push-Location $BuildDir

try {
    cmake $ProjectRoot "-DTARGET_PLATFORM=$Target"
    if ($LASTEXITCODE -ne 0) { throw "CMake configure failed" }
    cmake --build . -j
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
    Write-Host "Done. Binary: $BuildDir\desk_assistant" -ForegroundColor Green
} finally {
    Pop-Location
}
