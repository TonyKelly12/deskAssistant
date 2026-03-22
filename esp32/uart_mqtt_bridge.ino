/**
 * ESP32 UART ↔ MQTT bridge (conceptual)
 *
 * This ESP32 runs a minimal bridge: receives from UART, forwards conceptually
 * to your MQTT stack (or processes locally). Format matches Pi Zero 2.
 *
 * Protocol: "topic|payload\n"
 *
 * Wiring (ESP32 dev board to Pi Zero 2):
 *   ESP32 GPIO17 (UART2 TX) -> Pi GPIO15 (RXD)
 *   ESP32 GPIO16 (UART2 RX) -> Pi GPIO14 (TXD)
 *   GND -> GND
 *
 * Or use USB-Serial: Connect ESP32 USB to Pi Zero 2 USB (use /dev/ttyUSB0)
 *
 * For full MQTT on ESP32, use PubSubClient or ESP-IDF MQTT.
 * This sketch shows the UART protocol only.
 */

#define UART_RX_PIN 16  // UART2 RX on many ESP32 boards
#define UART_TX_PIN 17  // UART2 TX
#define UART_BAUD   115200

#include <HardwareSerial.h>

HardwareSerial Uart(2);

void setup() {
  Serial.begin(115200);
  Uart.begin(UART_BAUD, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
}

void loop() {
  // Read from UART (Pi Zero 2)
  if (Uart.available()) {
    String line = Uart.readStringUntil('\n');
    int pipe = line.indexOf('|');
    if (pipe > 0) {
      String topic = line.substring(0, pipe);
      String payload = line.substring(pipe + 1);

      // Process or forward to MQTT here
      Serial.printf("UART rx: [%s] %s\n", topic.c_str(), payload.c_str());

      // Example: echo back
      Uart.print(topic + "|ack:" + payload + "\n");
    }
  }

  // Example: send sensor data periodically
  static unsigned long last = 0;
  if (millis() - last > 5000) {
    last = millis();
    Uart.print("sensor/temp|23.5\n");  // placeholder - Pi adds esp32/ prefix when publishing
  }
}
