"""Map logical moves to UART topics your ESP32 understands — adjust topics to match firmware."""

from __future__ import annotations

# Example topic; change to match your bridge (e.g. servo/channel/us)


def set_channel_us(channel: int, microseconds: int) -> str:
    """Return a line body or topic|payload for one channel (customize)."""
    return f"{channel}|{microseconds}"


def center_all(num_channels: int = 16) -> list[str]:
    """Placeholder: center pulse width in µs — tune for your hardware."""
    center_us = 1500
    return [set_channel_us(ch, center_us) for ch in range(num_channels)]
