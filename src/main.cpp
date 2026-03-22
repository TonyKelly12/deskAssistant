#include "mqtt_client.hpp"
#include "uart_bridge.hpp"
#include <iostream>
#include <csignal>
#include <chrono>
#include <thread>

#if defined(TARGET_PI_ZERO_2)
constexpr const char* PLATFORM_NAME = "Pi Zero 2";
#elif defined(TARGET_JETSON_ORIN_NANO)
constexpr const char* PLATFORM_NAME = "Jetson Orin Nano";
#else
constexpr const char* PLATFORM_NAME = "Native";
#endif

static volatile std::sig_atomic_t g_running = 1;

void signal_handler(int signum) {
    if (signum == SIGINT || signum == SIGTERM) {
        g_running = 0;
    }
}

int main(int argc, char* argv[]) {
    std::cout << "DeskAssistant MQTT Client - " << PLATFORM_NAME << std::endl;

    // Configuration - can be overridden via environment or config file
    const char* broker_host = std::getenv("MQTT_BROKER_HOST");
    if (!broker_host) broker_host = "localhost";

    const char* broker_port_str = std::getenv("MQTT_BROKER_PORT");
    int broker_port = broker_port_str ? std::atoi(broker_port_str) : 1883;

    // Client ID includes platform for debugging
    std::string client_id = "desk_assistant_";
    client_id += PLATFORM_NAME;
    for (auto& c : client_id) {
        if (c == ' ') c = '_';
    }

    desk::MqttClient client(client_id);
    client.setBroker(broker_host, broker_port);

    // Optional: credentials if broker requires auth
    const char* mqtt_user = std::getenv("MQTT_USERNAME");
    const char* mqtt_pass = std::getenv("MQTT_PASSWORD");
    if (mqtt_user && mqtt_pass) {
        client.setCredentials(mqtt_user, mqtt_pass);
    }

    desk::UartBridge uart;
#if defined(TARGET_PI_ZERO_2)
    const char* uart_dev = std::getenv("UART_DEVICE");
    const char* uart_baud_str = std::getenv("UART_BAUD");
    int uart_baud = uart_baud_str ? std::atoi(uart_baud_str) : 115200;
    if (uart_dev && uart.open(uart_dev, uart_baud)) {
        uart.setMessageCallback([&client](const std::string& topic, const std::string& payload) {
            std::cout << "UART->MQTT [" << topic << "] " << payload << std::endl;
            client.publish("esp32/" + topic, payload);
        });
    }
#endif

    client.setMessageCallback([&client, &uart](const std::string& topic, const std::string& payload) {
        std::cout << "[" << topic << "] " << payload << std::endl;

        // Example: echo back on command topic
        if (topic == "desk/command" && payload == "ping") {
            client.publish("desk/response", "pong");
        }
        // Forward MQTT messages for ESP32 to UART (Pi Zero 2 only)
        if (topic.find("esp32/") == 0 && uart.isOpen()) {
            std::string uart_topic = topic.substr(6);
            uart.send(uart_topic, payload);
        }
    });

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    if (!client.connect()) {
        std::cerr << "Failed to connect to broker at " << broker_host << ":" << broker_port
                  << "\nEnsure Mosquitto broker is running. See README for setup." << std::endl;
        return 1;
    }

    client.subscribe("desk/command");
    client.subscribe("desk/status");
    client.subscribe("esp32/#");

    std::cout << "Subscribed to desk/command, desk/status, esp32/#. Press Ctrl+C to exit." << std::endl;

    while (g_running && client.loop(1000)) {
#if defined(TARGET_PI_ZERO_2)
        if (uart.isOpen()) uart.poll();
#endif
        // Publish heartbeat periodically
        static auto last_heartbeat = std::chrono::steady_clock::now();
        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - last_heartbeat).count() >= 30) {
            client.publish("desk/heartbeat", PLATFORM_NAME);
            last_heartbeat = now;
        }
    }

    client.disconnect();
    std::cout << "Shutdown complete." << std::endl;
    return 0;
}
