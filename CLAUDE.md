# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DeskAssistant is a multi-component embedded robotics project. It connects a **Raspberry Pi Zero 2** and **NVIDIA Jetson Orin Nano** via MQTT, with an **ESP32** bridged over UART. The stack has three main components:

1. **C++ MQTT client** (`src/`, `include/`) — runs on Pi Zero 2 or Jetson, built with CMake + libmosquitto
2. **Pi bot brain** (`pi/bot_brain/`) — Python controlling screen, ESP32 serial link, and emotions library; Pi-specific scripts in `pi/scripts/`
3. **Reporting API** (`reporting-api/`) — FastAPI service on Jetson that ingests MQTT and exposes REST

ESP32 sketches live in `esp32/` and are uploaded via Arduino IDE. To deploy to the Pi, sync only the `pi/` directory.

## Build Commands (C++ client)

```bash
# Native build (on host or target device)
./scripts/build-native.sh              # default: native
./scripts/build-native.sh pi_zero_2    # with Pi-specific defines
./scripts/build-native.sh jetson_orin_nano

# Cross-compile from Linux host
./scripts/build-pi-zero-2.sh           # armhf toolchain
./scripts/build-jetson-orin-nano.sh    # aarch64 toolchain

# CMake directly
cmake -B build -DTARGET_PLATFORM=pi_zero_2 -DCMAKE_TOOLCHAIN_FILE=cmake/toolchain-pi-zero-2.cmake
cmake --build build
```

Binary output: `build/desk_assistant`

Cross-compile requires `gcc-arm-linux-gnueabihf` (Pi) or `gcc-aarch64-linux-gnu` (Jetson) and `libmosquitto-dev`.

## Run Commands

```bash
# C++ MQTT client
./desk_assistant
MQTT_BROKER_HOST=192.168.1.10 MQTT_BROKER_PORT=1883 ./desk_assistant
MQTT_USERNAME=user MQTT_PASSWORD=pass ./desk_assistant

# Pi Zero 2 with UART bridge to ESP32
UART_DEVICE=/dev/ttyS0 UART_BAUD=115200 ./desk_assistant

# Reporting API (Jetson)
cd reporting-api
pip install -r requirements.txt
python main.py                           # FastAPI at http://localhost:8000
uvicorn main:app --host 0.0.0.0 --port 8000

# Pi bot brain
cd pi/bot_brain
python main.py

# Screen test (run on Pi after rsync)
bash pi/scripts/setup_display_venv_pi.sh
source .venv-display/bin/activate
python3 pi/scripts/spi_display_scaffold.py

# MQTT manual testing
mosquitto_sub -h localhost -t "desk/#" -v
mosquitto_pub -h localhost -t "desk/command" -m "ping"
```

## Architecture

### UART Protocol
All Pi↔ESP32 serial communication uses `topic|payload\n` format (defined in `include/uart_protocol.hpp`). The Pi C++ client bridges UART messages to MQTT under the `esp32/` prefix. The Python `Esp32Link` class (`pi/bot_brain/esp32_connection/link.py`) uses the same encoding. ESP32 sketches also implement this format.

### MQTT Topics
- `desk/command`, `desk/response`, `desk/heartbeat`, `desk/status` — core desk client topics
- `esp32/#` — bidirectional bridge: Pi receives from MQTT and forwards to UART; ESP32 UART messages are published under `esp32/`
- `sensors/temp/{source}`, `equipment/{id}/temp`, `equipment/{id}/error`, `equipment/{id}/stats/{key}` — reporting API topics

### Conditional Compilation
`TARGET_PLATFORM` cmake variable sets `TARGET_PI_ZERO_2=1` or `TARGET_JETSON_ORIN_NANO=1` preprocessor defines. UART bridge code in `src/main.cpp` and `src/uart_bridge.cpp` is guarded by `#if defined(TARGET_PI_ZERO_2)`.

### Reporting API Data Flow
`reporting-api/mqtt_handler.py` parses incoming MQTT topic patterns and routes to `store.py` (`ReportingStore`). The FastAPI app in `main.py` starts the paho-mqtt client in a background thread on startup and exposes REST endpoints at `/api/{temperature,errors,statistics,sources,raw}`.

### Pi Bot Brain
`pi/bot_brain/` is a Python package scaffold. Submodules are mostly stubs awaiting implementation:
- `screen/display.py` — GC9A01 SPI display (hook real driver here)
- `esp32_connection/link.py` — serial link using pyserial
- `emotions_library/catalog.py` — emotion catalog
- `servo_commands/commands.py` — servo control via ESP32 PCA9685

### ESP32 Sketches
- `uart_mqtt_bridge.ino` — reference UART↔MQTT bridge sketch
- `pca9685_servo/` — servo control via PCA9685 I2C board
- `ps4_controller/` — PS4 controller host
- `uart_blink_test.ino` / `scripts/pi_blink_test.py` — hardware comms verification

## Configuration

Copy `.env.example` files before running services:
- `config/desk-assistant.env.example` → `/etc/desk-assistant/env`
- `reporting-api/config/reporting-api.env.example` → configure before running

Systemd service files: `config/desk-assistant.service`, `reporting-api/config/reporting-api.service`
