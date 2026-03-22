# DeskAssistant Reporting API

Runs on the **Jetson Orin Nano**. Subscribes to MQTT topics from ESP32s, sensors, and equipment, then exposes a REST API to pull temperature, errors, and statistics.

## Prerequisites

- Jetson Orin Nano (or any Linux with Python 3.10+)
- Mosquitto MQTT broker running (typically on same Jetson)
- Python 3.10+

```bash
pip install -r requirements.txt
```

## Run

```bash
# Default: localhost:8000, MQTT at localhost:1883
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## REST Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/temperature` | All temperature readings |
| `GET /api/temperature/{source}` | Temperature from specific source |
| `GET /api/errors` | Recent errors (`?limit=50`) |
| `GET /api/statistics` | Statistics from all sources |
| `GET /api/statistics?source=lathe` | Statistics from one source |
| `GET /api/sources` | List known sources and metric types |
| `GET /api/raw` | Last message per topic (debug) |

## MQTT Topic Conventions

The API parses these topic patterns and routes to the appropriate endpoints:

| Topic | Maps to |
|-------|---------|
| `sensors/temp/{source}` | Temperature |
| `sensors/temperature/{source}` | Temperature |
| `equipment/{id}/temp` | Temperature |
| `equipment/{id}/temperature` | Temperature |
| `equipment/{id}/error` | Errors |
| `equipment/{id}/stats/{key}` | Statistics |
| `esp32/{path}` | From UART bridge (e.g. `esp32/sensor/temp`) |
| `desk/error` | Errors |
| `desk/stats/{key}` | Statistics |
| `{source}/temp` | Temperature (generic) |
| `{source}/error` | Errors (generic) |

### ESP32 Publishing Examples

**Temperature:**
```cpp
// Publishes to esp32/sensor/temp -> GET /api/temperature returns esp32/sensor
client.publish("sensors/temp/lathe", "72.5");
client.publish("equipment/lathe/temp", "72.5");
```

**Errors:**
```cpp
client.publish("equipment/lathe/error", "Overload detected");
client.publish("esp32/errors/fault", "Sensor timeout");
```

**Statistics:**
```cpp
client.publish("equipment/lathe/stats/rpm", "1500");
client.publish("equipment/mill/stats/run_time", "3600");
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Bind address |
| `API_PORT` | `8000` | HTTP port |
| `MQTT_BROKER_HOST` | `localhost` | MQTT broker |
| `MQTT_BROKER_PORT` | `1883` | MQTT port |
| `MQTT_USERNAME` | - | Broker username |
| `MQTT_PASSWORD` | - | Broker password |

## Systemd Service

```bash
sudo cp config/reporting-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable reporting-api
sudo systemctl start reporting-api
```
