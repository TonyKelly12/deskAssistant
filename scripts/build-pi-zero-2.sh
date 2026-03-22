#!/bin/bash
# Build DeskAssistant for Raspberry Pi Zero 2 (armhf)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build-pi-zero-2"

echo "Building for Pi Zero 2 (armhf)..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake "$PROJECT_ROOT" \
    -DCMAKE_TOOLCHAIN_FILE="$PROJECT_ROOT/cmake/toolchain-pi-zero-2.cmake" \
    -DTARGET_PLATFORM=pi_zero_2

cmake --build . -j$(nproc)
echo "Done. Binary: $BUILD_DIR/desk_assistant"
