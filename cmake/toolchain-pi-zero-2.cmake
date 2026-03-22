# CMake toolchain for Raspberry Pi Zero 2
# Pi Zero 2: ARMv8-A Cortex-A53, typically 32-bit armhf OS
#
# Prerequisites (Ubuntu/Debian host):
#   sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
#
# For 64-bit Pi OS use toolchain-jetson-orin-nano.cmake (aarch64) instead
#
# Usage: cmake -DCMAKE_TOOLCHAIN_FILE=cmake/toolchain-pi-zero-2.cmake ..

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR armv7l)

# Cross-compiler
set(CMAKE_C_COMPILER arm-linux-gnueabihf-gcc)
set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)

# Sysroot - point to Pi Zero 2 rootfs if you have one (rsync from device)
# Uncomment and set if cross-compiling with target libraries
# set(CMAKE_SYSROOT /path/to/pi-zero-2-sysroot)
# set(CMAKE_FIND_ROOT_PATH ${CMAKE_SYSROOT})
# set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
# set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
# set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
# set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Optimize for Cortex-A53
set(CMAKE_C_FLAGS_INIT "-march=armv8-a -mtune=cortex-a53 -mfloat-abi=hard")
set(CMAKE_CXX_FLAGS_INIT "-march=armv8-a -mtune=cortex-a53 -mfloat-abi=hard")
