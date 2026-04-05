#!/usr/bin/env python3
"""
Pi Zero 2 ↔ ESP32 UART blink test.

- Pi sends "test/pi_blink" every 1 second → ESP32 blinks its LED (slow, ~1 Hz)
- ESP32 sends "test/esp_blink" every 400ms → Pi blinks its LED (fast, ~2.5 Hz)

Wiring: Pi GPIO14 (TXD) → ESP32 RX | Pi GPIO15 (RXD) → ESP32 TX | GND → GND
Pi LED on GPIO 17 (or add external LED + resistor to any GPIO)
ESP32: built-in LED on GPIO 2 (or external)

Run: sudo python3 scripts/pi_blink_test.py
(serial and GPIO need root, or add user to dialout/gpio)
"""
import argparse
import serial
import sys
import time

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False

PI_BLINK_TOPIC = "test/pi_blink"
ESP_BLINK_TOPIC = "test/esp_blink"
PI_SEND_INTERVAL = 1.0   # seconds - Pi sends this often
ESP_BLINK_FAST = 0.15   # seconds - Pi LED on time when ESP32 commands (fast blink)


def main():
    parser = argparse.ArgumentParser(description="Pi Zero 2 ↔ ESP32 UART blink test")
    parser.add_argument("-d", "--device", default="/dev/ttyS0", help="Serial device (default: /dev/ttyS0)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("-l", "--led", type=int, default=17, help="Pi LED GPIO (default: 17)")
    args = parser.parse_args()

    if HAS_GPIO:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(args.led, GPIO.OUT)
        print(f"LED on GPIO {args.led}")
    else:
        print("RPi.GPIO not found - LED blink disabled (run on Pi Zero 2)")

    try:
        ser = serial.Serial(args.device, args.baud, timeout=0.1)
        print(f"UART opened: {args.device} @ {args.baud}")
    except serial.SerialException as e:
        print(f"Failed to open {args.device}: {e}")
        print("Try: /dev/ttyAMA0, /dev/ttyUSB0, or add user to dialout group")
        sys.exit(1)

    rx_buffer = ""
    last_send = 0.0
    led_on_until = 0.0

    print("Starting. Pi sends every 1s -> ESP32 LED (slow). ESP32 sends every 400ms -> Pi LED (fast). Ctrl+C to stop.")
    print()

    try:
        while True:
            now = time.monotonic()

            # Send pi_blink every PI_SEND_INTERVAL seconds
            if now - last_send >= PI_SEND_INTERVAL:
                line = f"{PI_BLINK_TOPIC}|1\n"
                ser.write(line.encode())
                last_send = now

            # Read from UART
            data = ser.read(256)
            if data:
                rx_buffer += data.decode("utf-8", errors="replace")
                while "\n" in rx_buffer:
                    line, rx_buffer = rx_buffer.split("\n", 1)
                    if "|" in line:
                        topic, payload = line.split("|", 1)
                        if topic.strip() == ESP_BLINK_TOPIC:
                            if HAS_GPIO:
                                GPIO.output(args.led, GPIO.HIGH)
                                led_on_until = now + ESP_BLINK_FAST
                            print(".", end="", flush=True)

            # Turn off Pi LED after brief flash
            if HAS_GPIO and led_on_until > 0 and now >= led_on_until:
                GPIO.output(args.led, GPIO.LOW)
                led_on_until = 0

            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if HAS_GPIO:
            GPIO.output(args.led, GPIO.LOW)
            GPIO.cleanup()
        ser.close()


if __name__ == "__main__":
    main()
