"""
GC9A01 240x240 round display driver with emotion-driven eye animations.

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
import threading
import spidev
import RPi.GPIO as GPIO
import numpy as np
from PIL import Image, ImageDraw

from screen.animations import EyeStyle, get_style

WIDTH    = 240
HEIGHT   = 240
DC       = 24
RST      = 25
SPI_PORT = 0
SPI_CS   = 0
CX       = WIDTH // 2
CY       = HEIGHT // 2


class Screen:
    def __init__(self, spi_hz: int = 40_000_000) -> None:
        self._spi_hz = spi_hz
        self._spi: spidev.SpiDev | None = None
        self._ready = False
        self._current_style: EyeStyle = get_style("neutral")
        self._lock = threading.Lock()

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
    # Emotion integration
    # ------------------------------------------------------------------

    def set_emotion(self, emotion: str) -> None:
        """
        Switch to the eye style for a given emotion.
        Plays a smooth transition then holds the new style.
        """
        new_style = get_style(emotion)
        with self._lock:
            old_style = self._current_style
            self._current_style = new_style
        self._transition(old_style, new_style)

    def run_emotion_loop(self, engine) -> None:
        """
        Main display loop driven by an EmotionEngine.
        Registers an on_change callback and runs the eye animation
        for the current emotion until KeyboardInterrupt.

        engine: EmotionEngine instance (already started)
        """
        engine.on_change(lambda old, new, s: self.set_emotion(new))
        self.set_emotion(engine.get_state().current)

        try:
            while True:
                with self._lock:
                    style = self._current_style
                self._run_blink_cycle(style)
        except KeyboardInterrupt:
            pass

    # ------------------------------------------------------------------
    # Low-level animation
    # ------------------------------------------------------------------

    def show(self, image: Image.Image) -> None:
        """Push a 240x240 PIL image to the display."""
        if not self._ready:
            raise RuntimeError("Screen not set up — call setup() first")
        self._set_window()
        self._cmd(0x2C)
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

    def blink(self, style: EyeStyle | None = None) -> None:
        """Play one blink animation using the given or current style."""
        with self._lock:
            s = style or self._current_style
        steps = [0.0, 0.25, 0.6, 0.9, 1.0, 0.9, 0.6, 0.25, 0.0]
        delay = 1.0 / s.blink_speed
        for ratio in steps:
            self.show(self._draw_eye(s, extra_close=ratio))
            time.sleep(delay)

    # ------------------------------------------------------------------
    # Internal: animation helpers
    # ------------------------------------------------------------------

    def _run_blink_cycle(self, style: EyeStyle) -> None:
        """Show open eye, wait blink_interval, then blink once."""
        self.show(self._draw_eye(style))
        deadline = time.monotonic() + style.blink_interval
        while time.monotonic() < deadline:
            # Check if style changed mid-wait
            with self._lock:
                if self._current_style is not style:
                    return
            time.sleep(0.05)
        self.blink(style)

    def _transition(self, old: EyeStyle, new: EyeStyle, frames: int = 8) -> None:
        """Crossfade between two eye styles."""
        for i in range(frames + 1):
            t = i / frames
            blended = self._blend_styles(old, new, t)
            self.show(self._draw_eye(blended))
            time.sleep(1 / 30)

    def _blend_styles(self, a: EyeStyle, b: EyeStyle, t: float) -> EyeStyle:
        """Linearly interpolate between two EyeStyles."""
        def lerp(x, y): return x + (y - x) * t
        def lerp_color(ca, cb):
            return tuple(int(lerp(ca[i], cb[i])) for i in range(3))

        return EyeStyle(
            bg_color=lerp_color(a.bg_color, b.bg_color),
            iris_color=lerp_color(a.iris_color, b.iris_color),
            pupil_color=lerp_color(a.pupil_color, b.pupil_color),
            iris_radius=int(lerp(a.iris_radius, b.iris_radius)),
            pupil_radius=int(lerp(a.pupil_radius, b.pupil_radius)),
            top_lid=lerp(a.top_lid, b.top_lid),
            bottom_lid=lerp(a.bottom_lid, b.bottom_lid),
            brow_angle=lerp(a.brow_angle, b.brow_angle),
            pupil_offset=(
                int(lerp(a.pupil_offset[0], b.pupil_offset[0])),
                int(lerp(a.pupil_offset[1], b.pupil_offset[1])),
            ),
            highlight=b.highlight,
            blink_interval=b.blink_interval,
            blink_speed=b.blink_speed,
        )

    # ------------------------------------------------------------------
    # Internal: eye drawing
    # ------------------------------------------------------------------

    def _draw_eye(self, style: EyeStyle, extra_close: float = 0.0) -> Image.Image:
        """
        Draw eye using the given EyeStyle.
        extra_close: additional eyelid closure for blink animation (0-1).
        """
        img = Image.new("RGB", (WIDTH, HEIGHT), style.bg_color)
        draw = ImageDraw.Draw(img)

        ir = style.iris_radius
        pr = style.pupil_radius
        ox, oy = style.pupil_offset

        # Iris
        draw.ellipse(
            (CX - ir, CY - ir, CX + ir, CY + ir),
            fill=style.iris_color,
        )

        # Pupil
        draw.ellipse(
            (CX + ox - pr, CY + oy - pr, CX + ox + pr, CY + oy + pr),
            fill=style.pupil_color,
        )

        # Specular highlight
        if style.highlight:
            draw.ellipse(
                (CX + 15, CY - 30, CX + 30, CY - 15),
                fill=(255, 255, 255),
            )

        # Eyelids
        margin = 8
        top_close    = style.top_lid + extra_close
        bottom_close = style.bottom_lid + extra_close

        top_travel    = int(ir * 1.5 * top_close)
        bottom_travel = int(ir * 1.5 * bottom_close)

        # Top eyelid
        draw.ellipse(
            (margin, margin - top_travel,
             WIDTH - margin, CY + top_travel),
            fill=style.bg_color,
        )

        # Bottom eyelid
        draw.ellipse(
            (margin, CY - bottom_travel,
             WIDTH - margin, HEIGHT - margin + bottom_travel),
            fill=style.bg_color,
        )

        # Angry / focused brow (diagonal line across top eyelid)
        if style.brow_angle > 0:
            brow_drop = int(style.brow_angle * 40)
            draw.polygon(
                [
                    (margin, margin),
                    (CX, margin + brow_drop),
                    (CX, margin),
                ],
                fill=style.bg_color,
            )

        return img

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
