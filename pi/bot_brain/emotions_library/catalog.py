"""
Emotion definitions for the DeskAssistant bot.

Each emotion has:
  - label:       Human readable name
  - decay:       Points lost per second when not actively reinforced (0-1)
  - priority:    Tiebreaker when two emotions have equal score
  - forced:      If True, this emotion can only be set via force_state(),
                 not via the point system
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmotionDef:
    label: str
    decay: float   # points/second
    priority: int  # higher = wins tiebreaker
    forced: bool = False


# ---------------------------------------------------------------------------
# Scored emotions — driven by the point system
# ---------------------------------------------------------------------------
EMOTIONS: dict[str, EmotionDef] = {
    # --- Baseline ---
    "neutral": EmotionDef(
        label="Neutral", decay=0.0, priority=0
    ),

    # --- Positive ---
    "happy": EmotionDef(
        label="Happy", decay=0.5, priority=2
    ),
    "excited": EmotionDef(
        label="Excited", decay=1.0, priority=3
    ),
    "breakthrough": EmotionDef(
        label="Breakthrough", decay=2.0, priority=5
    ),

    # --- Productive ---
    "focused": EmotionDef(
        label="Focused", decay=0.3, priority=2
    ),
    "working": EmotionDef(
        label="Working", decay=0.2, priority=1
    ),
    "researching": EmotionDef(
        label="Researching", decay=0.2, priority=1
    ),
    "listening": EmotionDef(
        label="Listening", decay=1.0, priority=2
    ),
    "presenting": EmotionDef(
        label="Presenting", decay=0.5, priority=2
    ),

    # --- Negative ---
    "bored": EmotionDef(
        label="Bored", decay=0.1, priority=1
    ),
    "sad": EmotionDef(
        label="Sad", decay=0.3, priority=2
    ),
    "frustrated": EmotionDef(
        label="Frustrated", decay=0.4, priority=3
    ),
    "debugging": EmotionDef(
        label="Debugging", decay=0.2, priority=2
    ),
}

# ---------------------------------------------------------------------------
# Forced states — override the point system entirely
# Set via force_state(), cleared via clear_forced()
# ---------------------------------------------------------------------------
FORCED_STATES: dict[str, EmotionDef] = {
    "angry": EmotionDef(
        label="Angry", decay=0.0, priority=10, forced=True
    ),
    "sleepy": EmotionDef(
        label="Sleepy", decay=0.0, priority=10, forced=True
    ),
    "tired": EmotionDef(
        label="Tired", decay=0.0, priority=10, forced=True
    ),
    "broken": EmotionDef(
        label="Broken", decay=0.0, priority=10, forced=True
    ),
}

ALL_EMOTIONS = {**EMOTIONS, **FORCED_STATES}


def list_emotions() -> list[str]:
    return sorted(ALL_EMOTIONS.keys())


# ---------------------------------------------------------------------------
# Events — what each event does to the point scores
# Format: event_name -> {emotion: delta}
# Deltas are multiplied by the intensity passed to add_event()
# ---------------------------------------------------------------------------
EVENTS: dict[str, dict[str, float]] = {
    # Task management
    "task_complete":    {"happy": 30, "excited": 20, "bored": -20, "sad": -15, "frustrated": -10},
    "task_overdue":     {"sad": 25, "frustrated": 15, "happy": -20},
    "task_added":       {"excited": 15, "focused": 10, "bored": -10},
    "task_started":     {"focused": 20, "working": 25, "bored": -15},

    # Pomodoro
    "focus_start":      {"focused": 30, "working": 20, "bored": -20},
    "focus_end":        {"happy": 15, "focused": -20, "working": -20},
    "break_start":      {"happy": 10, "focused": -10},
    "break_end":        {"focused": 20, "working": 15},

    # Agent / AI activity
    "researching":      {"researching": 30, "focused": 10, "bored": -10},
    "working":          {"working": 30, "focused": 15, "bored": -15},
    "presenting":       {"presenting": 30, "excited": 10},
    "listening":        {"listening": 40, "focused": 10},
    "delegating":       {"working": 15, "researching": 10},

    # Debugging
    "debug_start":      {"debugging": 25, "focused": 15},
    "debug_error":      {"frustrated": 20, "debugging": 10, "happy": -10},
    "breakthrough":     {"breakthrough": 50, "happy": 30, "excited": 20,
                         "frustrated": -40, "debugging": -30, "sad": -20},

    # System / hardware events
    "error":            {"frustrated": 25, "sad": 10, "happy": -15},
    "idle":             {"bored": 10, "focused": -5, "working": -5},
    "interaction":      {"happy": 10, "bored": -15, "excited": 5},
    "streak":           {"excited": 25, "happy": 20},
}
