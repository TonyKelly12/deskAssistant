#!/bin/bash
# Build DeskAssistant natively (for development or when building ON the target device)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"

TARGET="${1:-native}"
echo "Building for $TARGET (native)..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake "$PROJECT_ROOT" -DTARGET_PLATFORM="$TARGET"
cmake --build . -j$(nproc)
echo "Done. Binary: $BUILD_DIR/desk_assistant"
