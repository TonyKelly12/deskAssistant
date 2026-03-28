/**
 * Minimal blink test for ESP32 dev boards.
 *
 * Most ESP32-WROOM DevKit boards: built-in LED is GPIO2 (LED may be active-high).
 * If nothing blinks, try LED_PIN 5, 18, or 19 — or wire an LED + resistor to a GPIO.
 */

#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  Serial.println("Blink test — LED should toggle every 500 ms");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);
}
