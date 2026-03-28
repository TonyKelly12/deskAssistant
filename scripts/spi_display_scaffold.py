#!/usr/bin/env python3
"""
SPI round TFT (GC9A01, 240×240) on Raspberry Pi — matches your wiring.

GC9A01 is not ILI9341/ST7789: different controller, square framebuffer, round
visible area. Use a GC9A01-specific driver (this script uses GC9A01 + spidev).

Wiring (3V3 logic):
  VCC  -> Pi 3V3 (pin 1)
  GND  -> Pi GND (pin 6)
  SCL  -> GPIO11 / SPI0 SCLK (pin 23)
  SDA  -> GPIO10 / SPI0 MOSI (pin 19)
  DC   -> GPIO24 (pin 18)
  CS   -> GPIO8  / SPI0 CE0 (pin 24)
  RST  -> GPIO25 (pin 22)

Enable SPI: sudo raspi-config -> Interface Options -> SPI -> Enable

Dependencies (on the Pi):
  pip3 install spidev RPi.GPIO numpy pillow
  pip3 install "git+https://github.com/charliebruce/gc9a01-python.git#subdirectory=library"

If that git install fails, clone the repo and: pip3 install ./gc9a01-python/library
"""
from __future__ import annotations

import argparse
import sys

# SPI0 + CE0 (BCM8); control lines match your harness
SPI_PORT = 0
SPI_CS = 0
PIN_DC = 24
PIN_RST = 25
WIDTH = 240
HEIGHT = 240


def _make_display(rotation: int, spi_hz: int):
    try:
        from GC9A01 import GC9A01
    except ImportError as e:
        print(
            "Could not import GC9A01. Install:\n"
            "  pip3 install spidev RPi.GPIO numpy pillow\n"
            '  pip3 install "git+https://github.com/charliebruce/gc9a01-python.git#subdirectory=library"',
            file=sys.stderr,
        )
        raise SystemExit(1) from e

    return GC9A01(
        SPI_PORT,
        SPI_CS,
        dc=PIN_DC,
        rst=PIN_RST,
        backlight=None,
        width=WIDTH,
        height=HEIGHT,
        rotation=rotation,
        invert=True,
        spi_speed_hz=spi_hz,
    )


def run_demo(rotation: int, spi_hz: int) -> None:
    import RPi.GPIO as GPIO
    from PIL import Image, ImageDraw

    disp = _make_display(rotation, spi_hz)

    try:
        for color in ((0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 0)):
            img = Image.new("RGB", (WIDTH, HEIGHT), color)
            disp.display(img)

        img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 40))
        draw = ImageDraw.Draw(img)
        margin = 8
        draw.ellipse(
            (margin, margin, WIDTH - 1 - margin, HEIGHT - 1 - margin),
            outline=(220, 220, 220),
            width=3,
        )
        draw.text((16, 100), "GC9A01 OK", fill=(255, 255, 255))
        draw.text((16, 125), "240 round", fill=(180, 180, 200))
        disp.display(img)
    finally:
        GPIO.cleanup()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GC9A01 240x240 SPI round display (Pi SPI0, DC=24 RST=25 CE0)"
    )
    parser.add_argument(
        "--rotation",
        type=int,
        default=0,
        choices=(0, 90, 180, 270),
        help="Rotation in degrees (try 90 if image is wrong; library default is often 90)",
    )
    parser.add_argument(
        "--spi-mhz",
        type=float,
        default=16.0,
        help="SPI clock in MHz (default 16)",
    )
    args = parser.parse_args()
    spi_hz = int(args.spi_mhz * 1_000_000)

    run_demo(args.rotation, spi_hz)
    print(
        "Demo done. If colors/garbage are wrong, try --rotation 90 or lower --spi-mhz (e.g. 8)."
    )


if __name__ == "__main__":
    main()
