#!/bin/bash
# Build DeskAssistant for NVIDIA Jetson Orin Nano (aarch64)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build-jetson-orin-nano"

echo "Building for Jetson Orin Nano (aarch64)..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake "$PROJECT_ROOT" \
    -DCMAKE_TOOLCHAIN_FILE="$PROJECT_ROOT/cmake/toolchain-jetson-orin-nano.cmake" \
    -DTARGET_PLATFORM=jetson_orin_nano

cmake --build . -j$(nproc)
echo "Done. Binary: $BUILD_DIR/desk_assistant"
