/**
 * Portable PS4 (DualShock 4) Bluetooth host helpers for ESP32.
 *
 * Depends on Arduino library: "PS4Controller" (aed3/PS4-esp32, GitHub).
 * Board: ESP32 with Bluetooth Classic (BR/EDR), e.g. ESP32-WROOM. Not ESP32-C3.
 *
 * Pairing: the controller stores the host Bluetooth MAC (same idea as PS3).
 * Use a pairing tool / sixaxispairer workflow to set the controller's paired MAC
 * to this ESP32's address, or call printBluetoothMac() once and program that value.
 *
 * Differences vs PS3 stack: PS4 uses an RGB light bar (not 1–4 player LEDs),
 * rumble is small/large motors, and input is read from the global PS4 object.
 */

#pragma once

#include <Arduino.h>

namespace ps4_host {

/** Initialize BT and connect when the controller has this host MAC stored ("aa:bb:cc:dd:ee:ff"). */
bool begin(const char* controllerStoredHostMac);

/** Start stack without overriding MAC (controller must already match ESP32 default BT MAC). */
bool beginWithDefaultMac();

void shutdown();

bool isConnected();

/** ESP32 Bluetooth MAC (for programming into the controller). Works before begin(). */
void printBluetoothMac(Print& out);

void setOnInput(void (*callback)());
void setOnConnect(void (*callback)());
void setOnDisconnect(void (*callback)());

/** Light bar color; pushes output to the pad. */
void setLightBar(uint8_t r, uint8_t g, uint8_t b);

/** Motor strengths 0–255; pushes output to the pad. */
void setRumble(uint8_t smallMotor, uint8_t largeMotor);

/** Optional LED flash timing; pushes output to the pad. */
void setFlashRate(uint8_t onTimeMs, uint8_t offTimeMs);

}  // namespace ps4_host
