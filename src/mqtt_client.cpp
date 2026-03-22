#include "mqtt_client.hpp"
#include <mosquitto.h>  // for mosquitto_strerror
#include <cstring>
#include <iostream>

#ifdef TARGET_PI_ZERO_2
#include <iostream>
// Pi Zero 2: ARM Cortex-A53, lower power - enable lightweight options if needed
#endif

#ifdef TARGET_JETSON_ORIN_NANO
// Jetson Orin Nano: more capable, can use full feature set
#endif

namespace desk {

MqttClient::MqttClient(const std::string& client_id)
    : mosqpp::mosquittopp(client_id.c_str()) {
    mosqpp::lib_init();
}

MqttClient::~MqttClient() {
    disconnect();
    mosqpp::lib_cleanup();
}

void MqttClient::setBroker(const std::string& host, int port) {
    broker_host_ = host;
    broker_port_ = port;
}

void MqttClient::setCredentials(const std::string& username, const std::string& password) {
    username_pw_set(username.c_str(), password.c_str());
}

void MqttClient::setMessageCallback(MessageCallback cb) {
    msg_callback_ = std::move(cb);
}

bool MqttClient::connect() {
    int rc = mosqpp::mosquittopp::connect(broker_host_.c_str(), broker_port_, 60);
    if (rc != MOSQ_ERR_SUCCESS) {
        std::cerr << "MQTT connect failed: " << mosquitto_strerror(rc) << std::endl;
        return false;
    }
    return true;
}

void MqttClient::disconnect() {
    if (connected_) {
        mosqpp::mosquittopp::disconnect();
        connected_ = false;
    }
}

int MqttClient::publish(const std::string& topic, const std::string& payload, bool retain) {
    return publish(topic, payload.data(), payload.size(), retain);
}

int MqttClient::publish(const std::string& topic, const void* payload, size_t len, bool retain) {
    int rc = mosqpp::mosquittopp::publish(nullptr, topic.c_str(), static_cast<int>(len),
                                          payload, 1, retain);
    if (rc != MOSQ_ERR_SUCCESS) {
        std::cerr << "MQTT publish failed: " << mosquitto_strerror(rc) << std::endl;
    }
    return rc;
}

int MqttClient::subscribe(const std::string& topic, int qos) {
    int rc = mosqpp::mosquittopp::subscribe(nullptr, topic.c_str(), qos);
    if (rc != MOSQ_ERR_SUCCESS) {
        std::cerr << "MQTT subscribe failed: " << mosquitto_strerror(rc) << std::endl;
    }
    return rc;
}

bool MqttClient::loop(int timeout_ms) {
    int rc = mosqpp::mosquittopp::loop(timeout_ms);
    if (rc != MOSQ_ERR_SUCCESS && rc != MOSQ_ERR_NO_CONN) {
        std::cerr << "MQTT loop error: " << mosquitto_strerror(rc) << std::endl;
        return false;
    }
    return true;
}

void MqttClient::on_connect(int rc) {
    if (rc == 0) {
        connected_ = true;
        std::cout << "MQTT connected to " << broker_host_ << ":" << broker_port_ << std::endl;
    } else {
        connected_ = false;
        std::cerr << "MQTT connection failed: " << mosquitto_strerror(rc) << std::endl;
    }
}

void MqttClient::on_disconnect(int rc) {
    connected_ = false;
    if (rc != 0) {
        std::cerr << "MQTT disconnected: " << mosquitto_strerror(rc) << std::endl;
    }
}

void MqttClient::on_message(const struct mosquitto_message* msg) {
    if (!msg || !msg_callback_) return;

    std::string topic(msg->topic);
    std::string payload;
    if (msg->payload && msg->payloadlen > 0) {
        payload.assign(static_cast<const char*>(msg->payload),
                       static_cast<size_t>(msg->payloadlen));
    }
    msg_callback_(topic, payload);
}

} // namespace desk
