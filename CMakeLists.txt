cmake_minimum_required(VERSION 3.16)
project(DeskAssistant LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Platform configuration - set via -DTARGET_PLATFORM=pi_zero_2|jetson_orin_nano|native
if(NOT DEFINED TARGET_PLATFORM)
    set(TARGET_PLATFORM "native" CACHE STRING "Target: pi_zero_2, jetson_orin_nano, or native")
endif()

message(STATUS "Building for target: ${TARGET_PLATFORM}")

# Platform-specific defines (useful for conditional compilation)
if(TARGET_PLATFORM STREQUAL "pi_zero_2")
    add_compile_definitions(TARGET_PI_ZERO_2=1)
elseif(TARGET_PLATFORM STREQUAL "jetson_orin_nano")
    add_compile_definitions(TARGET_JETSON_ORIN_NANO=1)
endif()

# Find Mosquitto - libmosquitto and mosquittopp (C++ wrapper)
find_package(PkgConfig REQUIRED)
pkg_check_modules(MOSQUITTO REQUIRED mosquitto)

pkg_check_modules(MOSQUITTOPP REQUIRED mosquittopp)

add_executable(desk_assistant
    src/main.cpp
    src/mqtt_client.cpp
    src/uart_bridge.cpp
)

target_include_directories(desk_assistant PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${MOSQUITTO_INCLUDE_DIRS}
    ${MOSQUITTOPP_INCLUDE_DIRS}
)

target_link_libraries(desk_assistant
    ${MOSQUITTO_LIBRARIES}
    ${MOSQUITTOPP_LIBRARIES}
)

# Install target
install(TARGETS desk_assistant DESTINATION bin)
install(FILES config/mosquitto.conf DESTINATION etc/mosquitto RENAME mosquitto_desk_assistant.conf OPTIONAL)
