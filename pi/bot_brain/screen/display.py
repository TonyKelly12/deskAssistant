"""
GC9A01 240x240 round display driver with eye animation.

Wiring (Yeluft board):
  VCC -> Pi 3V3 (pin 1)
  GND -> Pi GND (pin 6)
  SCL -> GPIO11 / SPI0 SCLK (pin 23)
  SDA -> GPIO10 / SPI0 MOSI (pin 19)
  DC  -> GPIO24 (pin 18)
  RST -> GPIO25 (pin 22)
  CS  -> DO NOT CONNECT (board has CS tied LOW internally)
"""
from __future__ import annotations

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw

WIDTH  = 240
HEIGHT = 240
DC     = 24
RST    = 25
SPI_PORT = 0
SPI_CS   = 0


class Screen:
    def __init__(self, spi_hz: int = 40_000_000) -> None:
        self._spi_hz = spi_hz
        self._spi: spidev.SpiDev | None = None
        self._ready = False

    # ------------------------------------------------------------------
    # Setup / teardown
    # ------------------------------------------------------------------

    def setup(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DC, GPIO.OUT)
        GPIO.setup(RST, GPIO.OUT)

        self._spi = spidev.SpiDev()
        self._spi.open(SPI_PORT, SPI_CS)
        self._spi.max_speed_hz = self._spi_hz
        self._spi.mode = 0

        self._reset()
        self._init()
        self._ready = True

    def close(self) -> None:
        if self._spi:
            self._spi.close()
        GPIO.cleanup()
        self._ready = False

    @property
    def ready(self) -> bool:
        return self._ready

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def show(self, image: Image.Image) -> None:
        """Push a 240x240 PIL image to the display."""
        if not self._ready:
            raise RuntimeError("Screen not set up — call setup() first")
        self._set_window()
        self._cmd(0x2C)
        import numpy as np
        arr = np.array(image.convert("RGB"), dtype=np.uint8)
        r = arr[:, :, 0].astype(np.uint16)
        g = arr[:, :, 1].astype(np.uint16)
        b = arr[:, :, 2].astype(np.uint16)
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        hi = (rgb565 >> 8).astype(np.uint8)
        lo = (rgb565 & 0xFF).astype(np.uint8)
        interleaved = np.empty((WIDTH * HEIGHT * 2,), dtype=np.uint8)
        interleaved[0::2] = hi.flatten()
        interleaved[1::2] = lo.flatten()
        GPIO.output(DC, GPIO.HIGH)
        data = interleaved.tolist()
        for i in range(0, len(data), 4096):
            self._spi.xfer2(data[i:i + 4096])

    # ------------------------------------------------------------------
    # Eye animation
    # ------------------------------------------------------------------

    def blink(self, fps: int = 24) -> None:
        """Play one blink animation (open -> close -> open)."""
        frames = self._build_blink_frames()
        delay = 1.0 / fps
        for frame in frames:
            self.show(frame)
            time.sleep(delay)

    def run_eyes(self, blink_interval: float = 3.0) -> None:
        """
        Loop forever: hold open eye, blink periodically.
        Call from a thread or main loop. Exits on KeyboardInterrupt.
        """
        open_frame = self._draw_eye(0.0)
        self.show(open_frame)
        last_blink = time.monotonic()
        try:
            while True:
                now = time.monotonic()
                if now - last_blink >= blink_interval:
                    self.blink()
                    last_blink = time.monotonic()
                    self.show(open_frame)
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass

    # ------------------------------------------------------------------
    # Internal: eye drawing
    # ------------------------------------------------------------------

    def _draw_eye(self, close_ratio: float) -> Image.Image:
        """
        Draw a single eye.
        close_ratio: 0.0 = fully open, 1.0 = fully closed.
        """
        img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 30))
        draw = ImageDraw.Draw(img)

        cx, cy = WIDTH // 2, HEIGHT // 2

        # Iris
        iris_r = 70
        draw.ellipse(
            (cx - iris_r, cy - iris_r, cx + iris_r, cy + iris_r),
            fill=(30, 120, 220),
        )

        # Pupil
        pupil_r = 35
        draw.ellipse(
            (cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r),
            fill=(10, 10, 10),
        )

        # Specular highlight
        draw.ellipse((cx + 15, cy - 30, cx + 30, cy - 15), fill=(255, 255, 255))

        # Eyelids — top and bottom grow toward center as close_ratio increases
        eyelid_travel = int(iris_r * 1.4 * close_ratio)
        margin = 10

        # Top eyelid
        draw.ellipse(
            (margin, margin - eyelid_travel,
             WIDTH - margin, cy + eyelid_travel),
            fill=(20, 20, 30),
        )
        # Bottom eyelid
        draw.ellipse(
            (margin, cy - eyelid_travel,
             WIDTH - margin, HEIGHT - margin + eyelid_travel),
            fill=(20, 20, 30),
        )

        return img

    def _build_blink_frames(self) -> list[Image.Image]:
        """Generate close + open frames for a blink."""
        steps = [0.0, 0.2, 0.5, 0.8, 1.0, 0.8, 0.5, 0.2, 0.0]
        return [self._draw_eye(r) for r in steps]

    # ------------------------------------------------------------------
    # Internal: SPI / display init
    # ------------------------------------------------------------------

    def _cmd(self, c: int) -> None:
        GPIO.output(DC, GPIO.LOW)
        self._spi.xfer2([c])

    def _dat(self, d: int | list) -> None:
        GPIO.output(DC, GPIO.HIGH)
        if isinstance(d, int):
            self._spi.xfer2([d])
        else:
            for i in range(0, len(d), 4096):
                self._spi.xfer2(d[i:i + 4096])

    def _reset(self) -> None:
        GPIO.output(RST, GPIO.HIGH); time.sleep(0.1)
        GPIO.output(RST, GPIO.LOW);  time.sleep(0.1)
        GPIO.output(RST, GPIO.HIGH); time.sleep(0.12)

    def _set_window(self, x0: int = 0, y0: int = 0,
                    x1: int = WIDTH - 1, y1: int = HEIGHT - 1) -> None:
        self._cmd(0x2A)
        self._dat([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self._cmd(0x2B)
        self._dat([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

    def _init(self) -> None:
        self._cmd(0xEF)
        self._cmd(0xEB); self._dat(0x14)
        self._cmd(0xFE)
        self._cmd(0xEF)
        self._cmd(0xEB); self._dat(0x14)
        self._cmd(0x84); self._dat(0x40)
        self._cmd(0x85); self._dat(0xFF)
        self._cmd(0x86); self._dat(0xFF)
        self._cmd(0x87); self._dat(0xFF)
        self._cmd(0x88); self._dat(0x0A)
        self._cmd(0x89); self._dat(0x21)
        self._cmd(0x8A); self._dat(0x00)
        self._cmd(0x8B); self._dat(0x80)
        self._cmd(0x8C); self._dat(0x01)
        self._cmd(0x8D); self._dat(0x01)
        self._cmd(0x8E); self._dat(0xFF)
        self._cmd(0x8F); self._dat(0xFF)
        self._cmd(0xB6); self._dat(0x00); self._dat(0x00)
        self._cmd(0x36); self._dat(0x18)
        self._cmd(0x3A); self._dat(0x05)
        self._cmd(0x90); self._dat([0x08, 0x08, 0x08, 0x08])
        self._cmd(0xBD); self._dat(0x06)
        self._cmd(0xBC); self._dat(0x00)
        self._cmd(0xFF); self._dat([0x60, 0x01, 0x04])
        self._cmd(0xC3); self._dat(0x13)
        self._cmd(0xC4); self._dat(0x13)
        self._cmd(0xC9); self._dat(0x22)
        self._cmd(0xBE); self._dat(0x11)
        self._cmd(0xE1); self._dat([0x10, 0x0E])
        self._cmd(0xDF); self._dat([0x21, 0x0C, 0x02])
        self._cmd(0xF0); self._dat([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])
        self._cmd(0xF1); self._dat([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])
        self._cmd(0xF2); self._dat([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])
        self._cmd(0xF3); self._dat([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])
        self._cmd(0xED); self._dat([0x1B, 0x0B])
        self._cmd(0xAE); self._dat(0x77)
        self._cmd(0xCD); self._dat(0x63)
        self._cmd(0x70); self._dat([0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03])
        self._cmd(0xE8); self._dat(0x34)
        self._cmd(0x62); self._dat([0x18, 0x0D, 0x71, 0xED, 0x70, 0x70,
                                     0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70])
        self._cmd(0x63); self._dat([0x18, 0x11, 0x71, 0xF1, 0x70, 0x70,
                                     0x18, 0x13, 0x71, 0xF3, 0x70, 0x70])
        self._cmd(0x64); self._dat([0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07])
        self._cmd(0x66); self._dat([0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00])
        self._cmd(0x67); self._dat([0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98])
        self._cmd(0x74); self._dat([0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00])
        self._cmd(0x98); self._dat([0x3E, 0x07])
        self._cmd(0x35)
        self._cmd(0x21)
        self._cmd(0x11); time.sleep(0.12)
        self._cmd(0x29); time.sleep(0.02)
