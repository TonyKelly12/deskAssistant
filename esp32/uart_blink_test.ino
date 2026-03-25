/**
 * ESP32 ↔ Pi Zero 2 UART blink test
 *
 * - Pi sends "test/pi_blink" every 1 second → ESP32 blinks LED (SLOW, ~1 Hz)
 * - ESP32 sends "test/esp_blink" every 400ms → Pi blinks its LED (FAST, ~2.5 Hz)
 *
 * Wiring:
 *   ESP32 UART2 TX (GPIO17) → Pi GPIO15 (RXD)
 *   ESP32 UART2 RX (GPIO16) → Pi GPIO14 (TXD)
 *   GND → GND
 *
 * LED: Built-in LED on GPIO 2 (or change LED_PIN)
 *
 * Run pi_blink_test.py on the Pi, then upload this sketch to the ESP32.
 */
#define UART_RX_PIN  16
#define UART_TX_PIN  17
#define UART_BAUD    115200
#define LED_PIN      2   // Built-in LED on most ESP32 dev boards

#define PI_BLINK_TOPIC   "test/pi_blink"
#define ESP_BLINK_TOPIC "test/esp_blink"
#define PI_BLINK_INTERVAL_MS   1000   // Pi sends every 1s -> ESP32 LED slow
#define ESP_SEND_INTERVAL_MS   400    // ESP32 sends every 400ms -> Pi LED fast
#define LED_FLASH_MS           80    // Brief flash when we receive

#include <HardwareSerial.h>

HardwareSerial Uart(2);

unsigned long lastEspSend = 0;
unsigned long ledOffAt = 0;

void setup() {
  Serial.begin(115200);
  Uart.begin(UART_BAUD, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("ESP32 UART blink test - Pi sends slow, ESP32 sends fast");
}

void loop() {
  unsigned long now = millis();

  // ---- Receive from Pi ----
  if (Uart.available()) {
    String line = Uart.readStringUntil('\n');
    int pipe = line.indexOf('|');
    if (pipe > 0) {
      String topic = line.substring(0, pipe);
      if (topic == PI_BLINK_TOPIC) {
        digitalWrite(LED_PIN, HIGH);
        ledOffAt = now + LED_FLASH_MS;
        Serial.print("P");  // Pi commanded blink
      }
    }
  }

  // Turn off LED after flash
  if (ledOffAt > 0 && now >= ledOffAt) {
    digitalWrite(LED_PIN, LOW);
    ledOffAt = 0;
  }

  // ---- Send to Pi (so Pi blinks its LED fast) ----
  if (now - lastEspSend >= ESP_SEND_INTERVAL_MS) {
    lastEspSend = now;
    Uart.print(ESP_BLINK_TOPIC);
    Uart.print("|1\n");
  }

  delay(5);
}
