#!/usr/bin/env python3
"""
GC9A01 screen test using the carlfriess init sequence - works with
generic/clone boards like Yeluft that don't respond to the Waveshare sequence.

Wiring:
  VCC -> Pi 3V3 (pin 1)
  GND -> Pi GND (pin 6)
  SCL -> GPIO11 / SPI0 SCLK (pin 23)
  SDA -> GPIO10 / SPI0 MOSI (pin 19)
  DC  -> GPIO24 (pin 18)
  RST -> GPIO25 (pin 22)
  CS  -> DO NOT CONNECT (Yeluft board has CS tied LOW internally)
"""
import spidev
import RPi.GPIO as GPIO
import time

DC  = 24
RST = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 4000000
spi.mode = 0


def cmd(c):
    GPIO.output(DC, GPIO.LOW)
    spi.xfer2([c])


def dat(d):
    GPIO.output(DC, GPIO.HIGH)
    if isinstance(d, int):
        spi.xfer2([d])
    else:
        for i in range(0, len(d), 4096):
            spi.xfer2(list(d[i:i + 4096]))


def reset():
    GPIO.output(RST, GPIO.HIGH); time.sleep(0.1)
    GPIO.output(RST, GPIO.LOW);  time.sleep(0.1)
    GPIO.output(RST, GPIO.HIGH); time.sleep(0.12)


def init():
    reset()
    cmd(0xEF)
    cmd(0xEB); dat(0x14)
    cmd(0xFE)
    cmd(0xEF)
    cmd(0xEB); dat(0x14)
    cmd(0x84); dat(0x40)
    cmd(0x85); dat(0xFF)
    cmd(0x86); dat(0xFF)
    cmd(0x87); dat(0xFF)
    cmd(0x88); dat(0x0A)
    cmd(0x89); dat(0x21)
    cmd(0x8A); dat(0x00)
    cmd(0x8B); dat(0x80)
    cmd(0x8C); dat(0x01)
    cmd(0x8D); dat(0x01)
    cmd(0x8E); dat(0xFF)
    cmd(0x8F); dat(0xFF)
    cmd(0xB6); dat(0x00); dat(0x00)
    cmd(0x36); dat(0x18)         # MADCTL
    cmd(0x3A); dat(0x05)         # COLMOD: 16-bit RGB565
    cmd(0x90); dat(0x08); dat(0x08); dat(0x08); dat(0x08)
    cmd(0xBD); dat(0x06)
    cmd(0xBC); dat(0x00)
    cmd(0xFF); dat(0x60); dat(0x01); dat(0x04)
    cmd(0xC3); dat(0x13)
    cmd(0xC4); dat(0x13)
    cmd(0xC9); dat(0x22)
    cmd(0xBE); dat(0x11)
    cmd(0xE1); dat(0x10); dat(0x0E)
    cmd(0xDF); dat(0x21); dat(0x0C); dat(0x02)
    cmd(0xF0); dat(0x45); dat(0x09); dat(0x08); dat(0x08); dat(0x26); dat(0x2A)
    cmd(0xF1); dat(0x43); dat(0x70); dat(0x72); dat(0x36); dat(0x37); dat(0x6F)
    cmd(0xF2); dat(0x45); dat(0x09); dat(0x08); dat(0x08); dat(0x26); dat(0x2A)
    cmd(0xF3); dat(0x43); dat(0x70); dat(0x72); dat(0x36); dat(0x37); dat(0x6F)
    cmd(0xED); dat(0x1B); dat(0x0B)
    cmd(0xAE); dat(0x77)
    cmd(0xCD); dat(0x63)
    cmd(0x70); dat(0x07); dat(0x07); dat(0x04); dat(0x0E); dat(0x0F); dat(0x09); dat(0x07); dat(0x08); dat(0x03)
    cmd(0xE8); dat(0x34)
    cmd(0x62)
    dat(0x18); dat(0x0D); dat(0x71); dat(0xED); dat(0x70); dat(0x70)
    dat(0x18); dat(0x0F); dat(0x71); dat(0xEF); dat(0x70); dat(0x70)
    cmd(0x63)
    dat(0x18); dat(0x11); dat(0x71); dat(0xF1); dat(0x70); dat(0x70)
    dat(0x18); dat(0x13); dat(0x71); dat(0xF3); dat(0x70); dat(0x70)
    cmd(0x64); dat(0x28); dat(0x29); dat(0xF1); dat(0x01); dat(0xF1); dat(0x00); dat(0x07)
    cmd(0x66); dat(0x3C); dat(0x00); dat(0xCD); dat(0x67); dat(0x45); dat(0x45); dat(0x10); dat(0x00); dat(0x00); dat(0x00)
    cmd(0x67); dat(0x00); dat(0x3C); dat(0x00); dat(0x00); dat(0x00); dat(0x01); dat(0x54); dat(0x10); dat(0x32); dat(0x98)
    cmd(0x74); dat(0x10); dat(0x85); dat(0x80); dat(0x00); dat(0x00); dat(0x4E); dat(0x00)
    cmd(0x98); dat(0x3E); dat(0x07)
    cmd(0x35)
    cmd(0x21)                    # Display inversion on
    cmd(0x11); time.sleep(0.12)  # Sleep out
    cmd(0x29); time.sleep(0.02)  # Display on


def fill(r, g, b):
    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    hi = (color >> 8) & 0xFF
    lo = color & 0xFF
    cmd(0x2A); dat(0x00); dat(0x00); dat(0x00); dat(0xEF)
    cmd(0x2B); dat(0x00); dat(0x00); dat(0x00); dat(0xEF)
    cmd(0x2C)
    GPIO.output(DC, GPIO.HIGH)
    chunk = bytes([hi, lo] * 1024)
    for _ in range(240 * 240 // 1024):
        spi.xfer2(list(chunk))


print('Initializing display...')
init()
print('Init done')

colors = [('RED', 255, 0, 0), ('GREEN', 0, 255, 0), ('BLUE', 0, 0, 255), ('WHITE', 255, 255, 255)]
for name, r, g, b in colors:
    fill(r, g, b)
    print(f'{name} - holding 5 seconds')
    time.sleep(5)

GPIO.cleanup()
spi.close()
print('Done')
