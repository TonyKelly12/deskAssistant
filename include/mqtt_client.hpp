#pragma once

#include <mosquittopp.h>
#include <string>
#include <functional>
#include <atomic>

namespace desk {

/**
 * MQTT client wrapper using Eclipse Mosquitto (mosquittopp).
 * Configurable for Pi Zero 2, Jetson Orin Nano, or native builds.
 */
class MqttClient : public mosqpp::mosquittopp {
public:
    using MessageCallback = std::function<void(const std::string& topic, const std::string& payload)>;

    explicit MqttClient(const std::string& client_id);
    ~MqttClient();

    // Non-copyable
    MqttClient(const MqttClient&) = delete;
    MqttClient& operator=(const MqttClient&) = delete;

    /**
     * Configure connection parameters. Call before connect().
     */
    void setBroker(const std::string& host, int port = 1883);
    void setCredentials(const std::string& username, const std::string& password);
    void setMessageCallback(MessageCallback cb);

    /**
     * Connect to broker. Returns true on success.
     */
    bool connect();
    void disconnect();

    /**
     * Publish message to topic.
     * Returns MOSQ_ERR_SUCCESS on success.
     */
    int publish(const std::string& topic, const std::string& payload, bool retain = false);
    int publish(const std::string& topic, const void* payload, size_t len, bool retain = false);

    /**
     * Subscribe to topic. MessageCallback will be invoked for received messages.
     */
    int subscribe(const std::string& topic, int qos = 1);

    /**
     * Process network events. Call in main loop.
     */
    bool loop(int timeout_ms = 1000);

    bool isConnected() const { return connected_; }

private:
    void on_connect(int rc) override;
    void on_disconnect(int rc) override;
    void on_message(const struct mosquitto_message* msg) override;

    std::string broker_host_;
    int broker_port_ = 1883;
    MessageCallback msg_callback_;
    std::atomic<bool> connected_{false};
};

} // namespace desk
