"""In-memory store for sensor data, errors, and statistics."""
from datetime import datetime
from collections import deque
from typing import Any
import threading


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


class ReportingStore:
    """Thread-safe store for reporting data from MQTT."""

    def __init__(self, error_buffer_size: int = 100, stat_history_size: int = 100):
        self._lock = threading.RLock()
        self._temperatures: dict[str, dict] = {}  # source -> {value, unit, updated_at}
        self._errors: deque[dict] = deque(maxlen=error_buffer_size)
        self._statistics: dict[str, deque] = {}  # source.key -> deque of {value, updated_at}
        self._raw_messages: dict[str, dict] = {}  # topic -> last message
        self._stat_history_size = stat_history_size

    def record_temperature(self, source: str, value: float, unit: str = "celsius") -> None:
        with self._lock:
            self._temperatures[source] = {
                "value": value,
                "unit": unit,
                "updated_at": _utc_now(),
            }

    def record_error(self, source: str, message: str, severity: str = "error", **extra: Any) -> None:
        with self._lock:
            entry = {
                "source": source,
                "message": message,
                "severity": severity,
                "updated_at": _utc_now(),
                **extra,
            }
            self._errors.append(entry)

    def record_statistic(self, source: str, key: str, value: float | int | str | bool) -> None:
        with self._lock:
            store_key = f"{source}:{key}"
            if store_key not in self._statistics:
                self._statistics[store_key] = deque(maxlen=self._stat_history_size)
            self._statistics[store_key].append({
                "value": value,
                "updated_at": _utc_now(),
            })

    def record_raw(self, topic: str, payload: str) -> None:
        with self._lock:
            self._raw_messages[topic] = {
                "payload": payload,
                "updated_at": _utc_now(),
            }

    def get_temperatures(self) -> dict[str, dict]:
        with self._lock:
            return dict(self._temperatures)

    def get_temperature(self, source: str) -> dict | None:
        with self._lock:
            return self._temperatures.get(source)

    def get_errors(self, limit: int | None = None) -> list[dict]:
        with self._lock:
            items = list(self._errors)
        if limit:
            items = items[-limit:]
        return list(reversed(items))

    def get_statistics(self, source: str | None = None) -> dict:
        with self._lock:
            result: dict = {}
            for store_key, history in self._statistics.items():
                src, key = store_key.split(":", 1)
                if source and src != source:
                    continue
                latest = history[-1] if history else None
                if latest:
                    if src not in result:
                        result[src] = {}
                    result[src][key] = {
                        "value": latest["value"],
                        "updated_at": latest["updated_at"],
                    }
            return result

    def get_all_raw(self) -> dict[str, dict]:
        with self._lock:
            return dict(self._raw_messages)

    def get_sources(self) -> dict[str, list[str]]:
        """Return known sources and their metric types."""
        with self._lock:
            sources: dict[str, list[str]] = {}
            for src in self._temperatures:
                sources.setdefault(src, []).append("temperature")
            for store_key in self._statistics:
                src = store_key.split(":", 1)[0]
                sources.setdefault(src, []).append("statistics")
            for entry in self._errors:
                src = entry.get("source", "unknown")
                sources.setdefault(src, []).append("errors")
            return sources
