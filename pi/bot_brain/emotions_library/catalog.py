"""Central list of emotion ids — extend as you define assets / servo poses."""

from __future__ import annotations

# Keys are stable IDs; values are human labels (optional metadata later)
EMOTIONS: dict[str, str] = {
    "neutral": "Neutral",
    "happy": "Happy",
    "curious": "Curious",
    "sleepy": "Sleepy",
}


def list_emotions() -> list[str]:
    return sorted(EMOTIONS.keys())
