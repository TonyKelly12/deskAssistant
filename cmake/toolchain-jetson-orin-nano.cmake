# CMake toolchain for NVIDIA Jetson Orin Nano
# Jetson Orin Nano: ARMv8.2-A Cortex-A78AE, aarch64
#
# Prerequisites (Ubuntu x86_64 host):
#   sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
#
# Sysroot: For full cross-compilation, sync sysroot from Jetson:
#   rsync -avz --rsync-path="sudo rsync" user@jetson-ip:/usr/include /path/to/sysroot/usr/
#   rsync -avz --rsync-path="sudo rsync" user@jetson-ip:/lib /path/to/sysroot/
#
# Or build natively on the Jetson for simpler workflow.
#
# Usage: cmake -DCMAKE_TOOLCHAIN_FILE=cmake/toolchain-jetson-orin-nano.cmake ..

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Cross-compiler
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

# Sysroot - uncomment if you have a Jetson sysroot
# set(CMAKE_SYSROOT /path/to/jetson-sysroot)
# set(CMAKE_FIND_ROOT_PATH ${CMAKE_SYSROOT})
# set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
# set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
# set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
# set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Optimize for ARMv8.2
set(CMAKE_C_FLAGS_INIT "-march=armv8.2-a")
set(CMAKE_CXX_FLAGS_INIT "-march=armv8.2-a")
