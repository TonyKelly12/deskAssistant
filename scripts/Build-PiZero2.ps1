# Cross-build for Raspberry Pi Zero 2 (armhf)
# Requires: WSL with cmake, gcc-arm-linux-gnueabihf, g++-arm-linux-gnueabihf, libmosquitto-dev
# Or run from Linux directly
param([switch]$UseWsl)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$BuildDir = Join-Path $ProjectRoot "build-pi-zero-2"

$Toolchain = Join-Path $ProjectRoot "cmake\toolchain-pi-zero-2.cmake"

if ($UseWsl) {
    Write-Host "Building via WSL for Pi Zero 2..."
    $WslPath = (wsl wslpath -a $ProjectRoot)
    wsl bash -c "cd '$WslPath' && ./scripts/build-pi-zero-2.sh"
} else {
    Write-Host "Building for Pi Zero 2 (armhf)..."
    New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
    Push-Location $BuildDir
    try {
        cmake $ProjectRoot "-DCMAKE_TOOLCHAIN_FILE=$Toolchain" "-DTARGET_PLATFORM=pi_zero_2"
        if ($LASTEXITCODE -ne 0) { throw "CMake configure failed" }
        cmake --build . -j
        if ($LASTEXITCODE -ne 0) { throw "Build failed" }
        Write-Host "Done. Binary: $BuildDir\desk_assistant" -ForegroundColor Green
    } finally {
        Pop-Location
    }
}
