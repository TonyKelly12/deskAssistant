#!/usr/bin/env python3
"""
Cycle through every emotion style on the display so you can see each one.
Run from ~/deskAssistant:
  source .venv-display/bin/activate
  python3 scripts/test_emotions_display.py
"""
import sys
import time
sys.path.insert(0, 'bot_brain')

from screen import Screen
from screen.animations import STYLES

screen = Screen()
screen.setup()
print("Display ready")

emotions = list(STYLES.keys())
hold = 3.0  # seconds per emotion

try:
    for emotion in emotions:
        print(f"  {emotion}")
        screen.set_emotion(emotion)
        screen.blink()
        time.sleep(hold)
finally:
    screen.close()
    print("Done")
