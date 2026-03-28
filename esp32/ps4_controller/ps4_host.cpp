/**
 * Implementation — include PS4Controller.h only here for easy reuse in other projects.
 */

#include "ps4_host.h"

#include <PS4Controller.h>

#include "esp_err.h"
#include "esp_mac.h"

namespace ps4_host {

bool begin(const char* controllerStoredHostMac) {
  if (controllerStoredHostMac == nullptr || controllerStoredHostMac[0] == '\0') {
    return false;
  }
  return PS4.begin(controllerStoredHostMac);
}

bool beginWithDefaultMac() {
  return PS4.begin();
}

void shutdown() {
  PS4.end();
}

bool isConnected() {
  return PS4.isConnected();
}

void printBluetoothMac(Print& out) {
  uint8_t mac[6];
  if (esp_read_mac(mac, ESP_MAC_BT) != ESP_OK) {
    out.println(F("(could not read Bluetooth MAC)"));
    return;
  }
  out.printf(
      "%02x:%02x:%02x:%02x:%02x:%02x\n",
      mac[0],
      mac[1],
      mac[2],
      mac[3],
      mac[4],
      mac[5]);
}

void setOnInput(void (*callback)()) {
  PS4.attach(callback);
}

void setOnConnect(void (*callback)()) {
  PS4.attachOnConnect(callback);
}

void setOnDisconnect(void (*callback)()) {
  PS4.attachOnDisconnect(callback);
}

void setLightBar(uint8_t r, uint8_t g, uint8_t b) {
  PS4.setLed(r, g, b);
  PS4.sendToController();
}

void setRumble(uint8_t smallMotor, uint8_t largeMotor) {
  PS4.setRumble(smallMotor, largeMotor);
  PS4.sendToController();
}

void setFlashRate(uint8_t onTimeMs, uint8_t offTimeMs) {
  PS4.setFlashRate(onTimeMs, offTimeMs);
  PS4.sendToController();
}

}  // namespace ps4_host
