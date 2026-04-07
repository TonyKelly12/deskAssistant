#!/usr/bin/env python3
import sys
sys.path.insert(0, 'bot_brain')
from emotions_library import EmotionEngine

engine = EmotionEngine()
engine.on_change(lambda old, new, s: print(f"  CHANGE: [{old}] -> [{new}]"))
engine.start()

print("=== Starting state ===")
print(engine.get_state().to_dict())

print("\n=== task_complete ===")
s = engine.add_event("task_complete")
print(f"  current: {s.current}")

print("\n=== debug_error x3 ===")
for _ in range(3):
    s = engine.add_event("debug_error")
print(f"  current: {s.current}")

print("\n=== breakthrough ===")
s = engine.add_event("breakthrough")
print(f"  current: {s.current}")

print("\n=== force angry (tipped over) ===")
s = engine.force_state("angry")
print(f"  current: {s.current}")

print("\n=== clear forced ===")
s = engine.clear_forced()
print(f"  current: {s.current}")

print("\n=== force sleepy (charging) ===")
s = engine.force_state("sleepy")
print(f"  current: {s.current}")

print("\n=== full scores ===")
for emotion, score in sorted(engine.get_state().scores.items()):
    if score > 0:
        print(f"  {emotion}: {score:.1f}")

engine.stop()
print("\nDone")
