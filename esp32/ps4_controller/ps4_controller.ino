/**
 * Example: PS4 (DualShock 4) over Bluetooth (ESP32 + PS4Controller library).
 *
 * 1. Install library "PS4Controller" (aed3/PS4-esp32) — Arduino Library Manager or GitHub ZIP.
 * 2. Program the controller's paired MAC to match this ESP32 (see Serial output), or use
 *    beginWithDefaultMac() after the controller already targets this board.
 * 3. Open Serial Monitor at 115200; power the controller and connect (PS button).
 *
 * Copy ps4_host.h + ps4_host.cpp into any sketch folder to reuse the wrapper.
 */

#include <PS4Controller.h>

#include "ps4_host.h"

// Set true once: prints ESP32 Bluetooth MAC — program that into the controller, then set false.
static constexpr bool USE_MAC_PRINT_MODE = true;

// MAC the controller is programmed to expect (after pairing tool step).
static constexpr const char* HOST_MAC = "00:11:22:33:44:55";

static void onConnected() {
  Serial.println(F("[PS4] connected"));
  ps4_host::setLightBar(0, 32, 80);
}

static void onDisconnected() {
  Serial.println(F("[PS4] disconnected"));
}

static void onInput() {
  static uint32_t lastPrint;
  if (millis() - lastPrint < 200) {
    return;
  }
  lastPrint = millis();
  Serial.printf(
      "L: %4d %4d  R: %4d %4d  cross:%u  battery:%u\n",
      PS4.LStickX(),
      PS4.LStickY(),
      PS4.RStickX(),
      PS4.RStickY(),
      (unsigned)PS4.Cross(),
      (unsigned)PS4.Battery());
}

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println(F("\nPS4 host example"));

  if (USE_MAC_PRINT_MODE) {
    Serial.print(F("Program this Bluetooth MAC into your PS4 controller: "));
    ps4_host::printBluetoothMac(Serial);
    Serial.println(F("Then set USE_MAC_PRINT_MODE false and HOST_MAC to that value."));
    if (!ps4_host::beginWithDefaultMac()) {
      Serial.println(F("ps4_host::beginWithDefaultMac failed"));
      return;
    }
  } else {
    if (!ps4_host::begin(HOST_MAC)) {
      Serial.println(F("ps4_host::begin failed — check HOST_MAC"));
      return;
    }
  }

  ps4_host::setOnConnect(onConnected);
  ps4_host::setOnDisconnect(onDisconnected);
  ps4_host::setOnInput(onInput);
}

void loop() {
  delay(5);
}
