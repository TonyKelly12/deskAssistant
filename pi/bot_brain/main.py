#!/usr/bin/env python3
"""
Proxy-brain entrypoint: wire screen, ESP32 link, emotions, and servo commands here.
"""
from __future__ import annotations

import sys


def main() -> None:
    # Lazy imports so you can run main before every submodule is implemented
    from esp32_connection import Esp32Link
    from screen import Screen
    from emotions_library import list_emotions
    import servo_commands

    print("bot_brain scaffold OK")
    print("  emotions:", ", ".join(list_emotions()) or "(none)")
    print("  servo_commands:", [x for x in dir(servo_commands) if not x.startswith("_")])

    _ = Esp32Link  # placeholder instance when you add serial
    _ = Screen


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
