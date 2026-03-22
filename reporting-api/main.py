"""
DeskAssistant Reporting API - runs on Jetson Orin Nano.

Ingests data from MQTT (ESP32, sensors, equipment) and exposes REST endpoints
for temperature, errors, and statistics.
"""
import threading
import sys

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import (
    API_HOST,
    API_PORT,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPICS,
    ERROR_BUFFER_SIZE,
    STAT_HISTORY_SIZE,
)
from store import ReportingStore
from mqtt_handler import handle_message

app = FastAPI(
    title="DeskAssistant Reporting API",
    description="Temperature, errors, and statistics from ESP32 and sensors",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = ReportingStore(
    error_buffer_size=ERROR_BUFFER_SIZE,
    stat_history_size=STAT_HISTORY_SIZE,
)


def on_mqtt_connect(client, userdata, flags, reason_code):
    if reason_code != 0:
        print(f"MQTT connection failed: {reason_code}")
        return
    print(f"MQTT connected to {MQTT_BROKER}:{MQTT_PORT}")
    for topic in MQTT_TOPICS:
        client.subscribe(topic)
        print(f"  subscribed: {topic}")


def on_mqtt_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")
    handle_message(store, msg.topic, payload)


def run_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="reporting_api")
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"MQTT error: {e}")
        sys.exit(1)


@app.on_event("startup")
def startup():
    """Start MQTT client in background thread."""
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    mqtt_thread.start()


# --- REST Endpoints ---


@app.get("/api/health")
def health():
    """Health check."""
    return {"status": "ok"}


@app.get("/api/temperature")
def get_temperatures():
    """All temperature readings."""
    return store.get_temperatures()


@app.get("/api/temperature/{source}")
def get_temperature(source: str):
    """Temperature from a specific source."""
    data = store.get_temperature(source)
    if data is None:
        raise HTTPException(status_code=404, detail=f"No temperature data for {source}")
    return data


@app.get("/api/errors")
def get_errors(limit: int | None = 50):
    """Recent errors from equipment and sensors."""
    return {"errors": store.get_errors(limit=limit)}


@app.get("/api/statistics")
def get_statistics(source: str | None = None):
    """Statistics from all or a specific source."""
    return store.get_statistics(source=source)


@app.get("/api/sources")
def get_sources():
    """List known sources and their metric types."""
    return store.get_sources()


@app.get("/api/raw")
def get_raw():
    """Last message per topic (for debugging)."""
    return store.get_all_raw()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
