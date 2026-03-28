/**
 * PCA9685 16-channel PWM scaffold for servos (ESP32 + Wire I2C).
 *
 * Hardware reality: the PCA9685 cannot tell if a servo is plugged in — it only
 * outputs PWM. Automatic "motor present" detection is not possible without extra
 * circuitry (e.g. current sense) or a servo with a feedback wire.
 *
 * This sketch:
 *   - Initializes the PCA9685 at 50 Hz (typical analog servo rate).
 *   - Provides helpers to set pulse width in microseconds.
 *   - Optional interactive test: pulses each channel; you confirm y/n on Serial
 *     so channelActive[] reflects what you actually saw.
 *   - Optional quick sweep: pulses every channel in sequence (visual only;
 *     does not set channelActive — use interactive mode for that).
 *
 * Library: install "Adafruit PWM Servo Driver Library" (Arduino Library Manager).
 *
 * Wiring (typical):
 *   PCA9685 VCC -> 3.3V or 5V (match your servo supply; separate servo power
 *   is recommended for many servos — common ground with ESP32).
 *   GND -> GND
 *   SDA -> GPIO21 (default ESP32 I2C0 SDA)
 *   SCL -> GPIO22 (default ESP32 I2C0 SCL)
 *   OE can be left floating or tied per module docs.
 */

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// --- I2C / board ---
static constexpr uint8_t PCA9685_ADDR = 0x40;  // default; change if A0–A5 strapped
static constexpr uint32_t I2C_FREQ_HZ = 400000;  // 400 kHz fast mode

// --- Servo timing (microseconds) — adjust for your servos ---
static constexpr uint16_t US_CENTER = 1500;
static constexpr uint16_t US_MIN = 1000;
static constexpr uint16_t US_MAX = 2000;

// --- Test pulse: small deflection from center (verify movement without travel limits) ---
static constexpr uint16_t US_TEST_DELTA = 200;

// Set true to walk through channels on Serial (115200) and mark active/inactive (y/n).
// Requires Serial Monitor open — otherwise use quick sweep first.
static constexpr bool RUN_INTERACTIVE_TEST_ON_BOOT = false;

// Set true to pulse ch 0..15 once at boot (visual only; no channelActive updates).
static constexpr bool RUN_QUICK_SWEEP_ON_BOOT = true;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(PCA9685_ADDR);

/** channelActive[ch] is only meaningful if you use interactive test or set manually. */
bool channelActive[16];

static uint16_t microsecondsToTicks(uint16_t microseconds) {
  const float freqHz = 50.0f;
  return (uint16_t)((float)microseconds * freqHz * 4096.0f / 1000000.0f);
}

void setServoMicroseconds(uint8_t channel, uint16_t microseconds) {
  if (channel > 15) {
    return;
  }
  uint16_t off = microsecondsToTicks(microseconds);
  if (off > 4095) {
    off = 4095;
  }
  pwm.setPWM(channel, 0, off);
}

void pulseChannelTest(uint8_t channel) {
  setServoMicroseconds(channel, US_CENTER);
  delay(120);
  setServoMicroseconds(channel, US_CENTER + US_TEST_DELTA);
  delay(200);
  setServoMicroseconds(channel, US_CENTER - US_TEST_DELTA);
  delay(200);
  setServoMicroseconds(channel, US_CENTER);
  delay(120);
}

void allChannelsOff() {
  for (uint8_t ch = 0; ch < 16; ch++) {
    pwm.setPWM(ch, 0, 0);
  }
}

void runQuickSweep() {
  Serial.println(F("Quick sweep: pulse on ch 0..15 (watch servos)"));
  for (uint8_t ch = 0; ch < 16; ch++) {
    Serial.printf("Channel %u\n", ch);
    pulseChannelTest(ch);
    delay(300);
  }
  Serial.println(F("Sweep done."));
}

void runInteractiveChannelTest() {
  Serial.println(F("Interactive test: each channel gets a short pulse."));
  Serial.println(F("Type y if that channel's servo moved, n if not, s to skip rest."));
  for (uint8_t ch = 0; ch < 16; ch++) {
    channelActive[ch] = false;
  }

  for (uint8_t ch = 0; ch < 16; ch++) {
    Serial.printf("\n>>> Channel %u — pulse now. Moved? (y/n/s): ", ch);
    pulseChannelTest(ch);

    while (Serial.available() == 0) {
      delay(10);
    }
    char c = (char)Serial.read();
    while (Serial.available() > 0) {
      Serial.read();
    }
    if (c == 's' || c == 'S') {
      Serial.println(F("skip"));
      break;
    }
    if (c == 'y' || c == 'Y') {
      channelActive[ch] = true;
      Serial.println(F("active"));
    } else {
      channelActive[ch] = false;
      Serial.println(F("inactive"));
    }
  }

  Serial.println(F("\nSummary (channel: active):"));
  for (uint8_t ch = 0; ch < 16; ch++) {
    Serial.printf("  %2u: %s\n", ch, channelActive[ch] ? "yes" : "no");
  }
}

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println(F("\nPCA9685 servo scaffold"));

  Wire.begin();
  Wire.setClock(I2C_FREQ_HZ);

  Wire.beginTransmission(PCA9685_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println(F("ERROR: PCA9685 not on I2C at this address. Check wiring, pull-ups, A0–A5."));
    while (true) {
      delay(1000);
    }
  }
  pwm.begin();

  pwm.setOscillatorFrequency(25000000);
  pwm.setPWMFreq(50);
  delay(10);

  for (uint8_t i = 0; i < 16; i++) {
    channelActive[i] = false;
  }

  if (RUN_INTERACTIVE_TEST_ON_BOOT) {
    runInteractiveChannelTest();
  } else if (RUN_QUICK_SWEEP_ON_BOOT) {
    runQuickSweep();
  } else {
    Serial.println(F("Idle: call runQuickSweep() or runInteractiveChannelTest() from code,"));
    Serial.println(F("or enable RUN_* flags at top of sketch."));
  }

  allChannelsOff();
}

void loop() {
  // Idle — extend with your application (read sensors, set channels from channelActive[]).
  delay(500);
}
