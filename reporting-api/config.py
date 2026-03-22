"""Configuration for the DeskAssistant Reporting API."""
import os

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# MQTT broker (typically localhost on Jetson where Mosquitto runs)
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", None)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", None)

# Topics to subscribe to (equipment, sensors, esp32 bridge)
MQTT_TOPICS = [
    "sensors/#",
    "equipment/#",
    "esp32/#",
    "desk/#",
]

# How many error entries to retain
ERROR_BUFFER_SIZE = 100

# How many stat samples per source to keep (for trends)
STAT_HISTORY_SIZE = 100
