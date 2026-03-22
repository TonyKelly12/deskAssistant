"""MQTT message handler - parses topics and routes to store."""
from store import ReportingStore


# Topic patterns: sensors/temp/{source}, equipment/{id}/error, equipment/{id}/stats/{key}, etc.
# Also: esp32/sensor/temp (from UART bridge), desk/...


def _parse_float(s: str) -> float | None:
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _parse_int(s: str) -> int | None:
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def handle_message(store: ReportingStore, topic: str, payload: str) -> None:
    """Route MQTT message to appropriate store methods based on topic."""
    parts = topic.split("/")
    store.record_raw(topic, payload)

    # sensors/temp/{source} or sensors/temperature/{source}
    if len(parts) >= 3 and parts[0] == "sensors":
        if parts[1] in ("temp", "temperature"):
            source = "/".join(parts[2:]) or "unknown"
            val = _parse_float(payload)
            if val is not None:
                store.record_temperature(source, val, "celsius")

    # equipment/{id}/temp or equipment/{id}/temperature
    if len(parts) >= 3 and parts[0] == "equipment":
        eq_id = parts[1]
        if parts[2] in ("temp", "temperature"):
            val = _parse_float(payload)
            if val is not None:
                store.record_temperature(eq_id, val, "celsius")
        elif parts[2] == "error":
            store.record_error(eq_id, payload, severity="error")
        elif len(parts) >= 4 and parts[2] == "stats":
            key = parts[3]
            if _parse_float(payload) is not None:
                store.record_statistic(eq_id, key, _parse_float(payload))
            elif _parse_int(payload) is not None:
                store.record_statistic(eq_id, key, _parse_int(payload))
            else:
                store.record_statistic(eq_id, key, payload)

    # esp32/{path} - from UART bridge, e.g. esp32/sensor/temp, esp32/errors/...
    if len(parts) >= 2 and parts[0] == "esp32":
        source = "esp32/" + parts[1]
        if len(parts) >= 4 and parts[2] in ("temp", "temperature"):
            val = _parse_float(payload)
            if val is not None:
                store.record_temperature(source, val, "celsius")
        elif len(parts) >= 3 and "error" in parts[-1].lower():
            store.record_error(source, payload, severity="error")
        else:
            key = parts[-1] if len(parts) >= 3 else "value"
            val = _parse_float(payload)
            if val is not None:
                store.record_statistic(source, key, val)
            elif _parse_int(payload) is not None:
                store.record_statistic(source, key, _parse_int(payload))
            else:
                store.record_statistic(source, key, payload)

    # desk/error, desk/stats/...
    if len(parts) >= 2 and parts[0] == "desk":
        source = "desk"
        if parts[1] == "error":
            store.record_error(source, payload, severity="error")
        elif len(parts) >= 3 and parts[1] == "stats":
            store.record_statistic(source, parts[2], payload)

    # Generic: {source}/temp, {source}/error - catch-all
    if len(parts) >= 2:
        source = parts[0]
        if parts[1] in ("temp", "temperature"):
            val = _parse_float(payload)
            if val is not None:
                store.record_temperature(source, val, "celsius")
        elif parts[1] == "error":
            store.record_error(source, payload, severity="error")
