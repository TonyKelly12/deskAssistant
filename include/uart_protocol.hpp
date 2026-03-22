#pragma once

#include <string>

namespace desk {

/**
 * UART protocol between Pi Zero 2 and ESP32.
 * Shared format so both sides can parse messages identically.
 *
 * Format: "topic|payload\n"
 *   - topic: MQTT-style topic (e.g. esp32/sensor/temp)
 *   - payload: UTF-8 string, no newlines or pipes
 *   - delimiter: pipe (|)
 *   - terminator: newline (\n)
 *
 * Example: "esp32/sensor/temp|23.5\n"
 *
 * ESP32 side: use Serial.print("topic|payload\n") and parse incoming lines.
 */
namespace uart_protocol {

inline std::string encode(const std::string& topic, const std::string& payload) {
    return topic + "|" + payload + "\n";
}

inline bool decode(const std::string& line, std::string& topic, std::string& payload) {
    size_t pos = line.find('|');
    if (pos == std::string::npos) return false;
    topic = line.substr(0, pos);
    payload = line.substr(pos + 1);
    return true;
}

} // namespace uart_protocol
} // namespace desk
