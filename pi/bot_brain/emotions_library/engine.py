"""
EmotionEngine — point-based emotion state machine for DeskAssistant.

Usage:
    from emotions_library.engine import EmotionEngine

    engine = EmotionEngine()
    engine.on_change(lambda old, new, state: print(f"{old} -> {new}"))
    engine.start()                        # begins background decay thread

    engine.add_event("task_complete")     # scored emotion
    engine.add_event("debug_error", intensity=1.5)
    engine.force_state("angry")           # override (tipped over, etc.)
    engine.clear_forced()                 # back to point system

    state = engine.get_state()            # full snapshot
    engine.stop()
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable

from emotions_library.catalog import (
    ALL_EMOTIONS,
    EMOTIONS,
    EVENTS,
    FORCED_STATES,
)

# Points clamp to this range
MIN_SCORE = 0.0
MAX_SCORE = 100.0

# How often the decay thread runs
TICK_INTERVAL = 1.0  # seconds

# Neutral score — emotions below this don't compete
ACTIVATION_THRESHOLD = 10.0

# Score neutral starts at so there's always a winner
NEUTRAL_BASE = 20.0


@dataclass
class EmotionState:
    """Snapshot of the engine at a point in time."""
    current: str
    forced: str | None
    scores: dict[str, float]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "current": self.current,
            "forced": self.forced,
            "scores": {k: round(v, 2) for k, v in self.scores.items()},
            "timestamp": self.timestamp,
        }


class EmotionEngine:
    def __init__(self) -> None:
        self._scores: dict[str, float] = {
            name: 0.0 for name in EMOTIONS
        }
        self._scores["neutral"] = NEUTRAL_BASE

        self._forced: str | None = None
        self._current: str = "neutral"

        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._running = False

        self._callbacks: list[Callable[[str, str, EmotionState], None]] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background decay thread."""
        self._running = True
        self._thread = threading.Thread(target=self._decay_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background decay thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    # ------------------------------------------------------------------
    # Public API — called by MCP server / Ollama tools
    # ------------------------------------------------------------------

    def add_event(self, event: str, intensity: float = 1.0) -> EmotionState:
        """
        Apply an event to the emotion scores.
        intensity: multiplier on all deltas (0.5 = mild, 1.0 = normal, 2.0 = strong)
        """
        if event not in EVENTS:
            raise ValueError(f"Unknown event: '{event}'. Valid: {sorted(EVENTS)}")

        deltas = EVENTS[event]
        with self._lock:
            for emotion, delta in deltas.items():
                if emotion in self._scores:
                    self._scores[emotion] = _clamp(
                        self._scores[emotion] + delta * intensity
                    )
            return self._resolve()

    def force_state(self, emotion: str) -> EmotionState:
        """
        Force a specific emotion, overriding the point system.
        Used for hardware events: tipped (angry), charging (sleepy),
        battery low (tired), system error (broken).
        """
        if emotion not in FORCED_STATES:
            raise ValueError(
                f"'{emotion}' is not a forced state. "
                f"Valid forced states: {sorted(FORCED_STATES)}"
            )
        with self._lock:
            self._forced = emotion
            return self._resolve()

    def clear_forced(self) -> EmotionState:
        """Return to point-system-driven emotion."""
        with self._lock:
            self._forced = None
            return self._resolve()

    def set_score(self, emotion: str, score: float) -> EmotionState:
        """Directly set an emotion's score (0-100). Useful for MCP resets."""
        if emotion not in EMOTIONS:
            raise ValueError(f"Unknown scored emotion: '{emotion}'")
        with self._lock:
            self._scores[emotion] = _clamp(score)
            return self._resolve()

    def reset(self) -> EmotionState:
        """Reset all scores to baseline."""
        with self._lock:
            for name in self._scores:
                self._scores[name] = 0.0
            self._scores["neutral"] = NEUTRAL_BASE
            self._forced = None
            return self._resolve()

    def get_state(self) -> EmotionState:
        """Return current state snapshot."""
        with self._lock:
            return self._snapshot()

    def on_change(
        self, callback: Callable[[str, str, EmotionState], None]
    ) -> None:
        """
        Register a callback fired when the dominant emotion changes.
        callback(old_emotion, new_emotion, state)
        """
        self._callbacks.append(callback)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _decay_loop(self) -> None:
        while self._running:
            time.sleep(TICK_INTERVAL)
            with self._lock:
                for name, defn in EMOTIONS.items():
                    if defn.decay > 0 and self._scores[name] > 0:
                        self._scores[name] = max(
                            0.0,
                            self._scores[name] - defn.decay * TICK_INTERVAL,
                        )
                # Neutral drifts back up when everything else is low
                total_non_neutral = sum(
                    v for k, v in self._scores.items() if k != "neutral"
                )
                if total_non_neutral < 20:
                    self._scores["neutral"] = min(
                        MAX_SCORE,
                        self._scores["neutral"] + 1.0 * TICK_INTERVAL,
                    )
                self._resolve()

    def _resolve(self) -> EmotionState:
        """
        Determine the current dominant emotion.
        Must be called with self._lock held.
        """
        old = self._current

        if self._forced:
            self._current = self._forced
        else:
            # Find highest scoring emotion above activation threshold
            candidates = {
                name: score
                for name, score in self._scores.items()
                if score >= ACTIVATION_THRESHOLD
            }
            if not candidates:
                self._current = "neutral"
            else:
                self._current = max(
                    candidates,
                    key=lambda n: (
                        candidates[n],
                        EMOTIONS[n].priority,
                    ),
                )

        state = self._snapshot()

        if old != self._current:
            for cb in self._callbacks:
                threading.Thread(
                    target=cb, args=(old, self._current, state), daemon=True
                ).start()

        return state

    def _snapshot(self) -> EmotionState:
        """Build a state snapshot. Must be called with self._lock held."""
        return EmotionState(
            current=self._current,
            forced=self._forced,
            scores=dict(self._scores),
        )


def _clamp(value: float) -> float:
    return max(MIN_SCORE, min(MAX_SCORE, value))
