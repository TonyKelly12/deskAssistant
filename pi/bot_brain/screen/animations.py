"""
Eye animation styles — one per emotion state.

EyeStyle defines how the eye looks and behaves for a given emotion.
The Screen class reads these to drive the display.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EyeStyle:
    # Colors
    bg_color:      tuple[int, int, int]   # background fill
    iris_color:    tuple[int, int, int]   # iris fill
    pupil_color:   tuple[int, int, int] = (10, 10, 10)

    # Sizes (relative to 240x240 canvas, center=120)
    iris_radius:   int = 70
    pupil_radius:  int = 35

    # Eyelid shape — 0.0 open, 1.0 closed
    # top_lid > 0 = drooping top lid (sleepy/bored)
    # top_lid < 0 = raised top lid (excited/wide)
    top_lid:       float = 0.0
    bottom_lid:    float = 0.0

    # Angry / focused brow angle — positive tilts inner edge down
    brow_angle:    float = 0.0

    # Pupil offset from center (x, y) — for looking directions
    pupil_offset:  tuple[int, int] = (0, 0)

    # Specular highlight
    highlight:     bool = True

    # Blink behavior
    blink_interval: float = 3.0   # seconds between blinks
    blink_speed:    int   = 24    # fps during blink animation

    # Transition
    transition_frames: int = 8    # frames when switching between emotions


# ---------------------------------------------------------------------------
# Emotion → style mapping
# ---------------------------------------------------------------------------

STYLES: dict[str, EyeStyle] = {

    "neutral": EyeStyle(
        bg_color=(20, 20, 30),
        iris_color=(30, 120, 220),
        iris_radius=70,
        pupil_radius=35,
        blink_interval=3.0,
    ),

    "happy": EyeStyle(
        bg_color=(25, 20, 30),
        iris_color=(50, 160, 255),
        iris_radius=72,
        pupil_radius=33,
        top_lid=-0.08,          # slightly raised — open wide
        bottom_lid=0.05,        # slight upward curve on bottom
        blink_interval=2.0,
        blink_speed=28,
    ),

    "excited": EyeStyle(
        bg_color=(20, 20, 40),
        iris_color=(0, 220, 255),
        iris_radius=78,         # larger iris
        pupil_radius=40,        # big pupil
        top_lid=-0.15,          # wide open
        blink_interval=1.2,
        blink_speed=32,
    ),

    "breakthrough": EyeStyle(
        bg_color=(20, 15, 35),
        iris_color=(255, 210, 0),   # gold
        iris_radius=80,
        pupil_radius=38,
        top_lid=-0.2,               # very wide
        blink_interval=0.8,
        blink_speed=36,
    ),

    "focused": EyeStyle(
        bg_color=(15, 20, 30),
        iris_color=(20, 100, 200),
        iris_radius=65,
        pupil_radius=28,            # small precise pupil
        top_lid=0.1,                # slight squint
        blink_interval=5.0,         # rarely blinks when focused
        blink_speed=20,
    ),

    "working": EyeStyle(
        bg_color=(15, 22, 28),
        iris_color=(30, 140, 180),
        iris_radius=67,
        pupil_radius=30,
        top_lid=0.08,
        blink_interval=4.0,
    ),

    "researching": EyeStyle(
        bg_color=(18, 15, 35),
        iris_color=(130, 80, 220),  # purple — thinking
        iris_radius=68,
        pupil_radius=32,
        pupil_offset=(0, -8),       # looking up
        blink_interval=4.0,
    ),

    "listening": EyeStyle(
        bg_color=(20, 20, 35),
        iris_color=(60, 150, 255),
        iris_radius=75,             # wide open
        pupil_radius=40,
        top_lid=-0.1,
        blink_interval=3.0,
    ),

    "presenting": EyeStyle(
        bg_color=(20, 20, 35),
        iris_color=(80, 180, 255),
        iris_radius=73,
        pupil_radius=34,
        top_lid=-0.05,
        blink_interval=2.5,
        blink_speed=26,
    ),

    "bored": EyeStyle(
        bg_color=(20, 20, 25),
        iris_color=(60, 80, 110),   # dull grey-blue
        iris_radius=62,
        pupil_radius=28,
        top_lid=0.25,               # heavy drooping eyelid
        bottom_lid=-0.05,
        blink_interval=1.5,         # frequent slow blinks
        blink_speed=16,
    ),

    "sad": EyeStyle(
        bg_color=(18, 18, 28),
        iris_color=(40, 80, 160),   # dim blue
        iris_radius=60,
        pupil_radius=26,
        top_lid=0.15,
        bottom_lid=0.1,             # droopy lower lid
        pupil_offset=(0, 5),        # looking slightly down
        blink_interval=2.5,
        blink_speed=18,
    ),

    "frustrated": EyeStyle(
        bg_color=(30, 15, 15),      # warm dark red tint
        iris_color=(220, 100, 20),  # orange
        iris_radius=68,
        pupil_radius=38,            # dilated
        top_lid=0.12,
        brow_angle=0.3,             # furrowed brow
        blink_interval=2.0,
        blink_speed=22,
    ),

    "debugging": EyeStyle(
        bg_color=(18, 18, 20),
        iris_color=(200, 160, 20),  # amber
        iris_radius=66,
        pupil_radius=30,
        top_lid=0.1,                # focused squint
        blink_interval=4.5,
    ),

    # --- Forced states ---

    "angry": EyeStyle(
        bg_color=(35, 10, 10),      # dark red
        iris_color=(220, 30, 30),   # red
        iris_radius=72,
        pupil_radius=42,            # very dilated
        top_lid=0.2,
        brow_angle=0.5,             # sharp angry brow
        blink_interval=1.0,
        blink_speed=30,
    ),

    "sleepy": EyeStyle(
        bg_color=(15, 15, 22),
        iris_color=(30, 60, 120),   # dim blue
        iris_radius=58,
        pupil_radius=22,            # tiny pupil
        top_lid=0.55,               # mostly closed
        bottom_lid=0.1,
        blink_interval=0.5,         # drifts closed constantly
        blink_speed=10,             # very slow blinks
    ),

    "tired": EyeStyle(
        bg_color=(18, 18, 22),
        iris_color=(50, 70, 100),
        iris_radius=62,
        pupil_radius=25,
        top_lid=0.3,                # half closed
        blink_interval=1.5,
        blink_speed=14,
    ),

    "broken": EyeStyle(
        bg_color=(0, 0, 0),
        iris_color=(180, 0, 0),     # red — error
        pupil_color=(0, 0, 0),
        iris_radius=65,
        pupil_radius=20,
        top_lid=0.0,
        highlight=False,
        blink_interval=0.3,         # erratic
        blink_speed=40,
    ),
}


def get_style(emotion: str) -> EyeStyle:
    """Return the EyeStyle for an emotion, falling back to neutral."""
    return STYLES.get(emotion, STYLES["neutral"])
