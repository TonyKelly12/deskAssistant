#pragma once

#include <string>
#include <functional>
#include <memory>
#include <atomic>

namespace desk {

/**
 * UART bridge for Pi Zero 2 ↔ ESP32 communication.
 * Uses Linux serial APIs (termios). Only compiled when TARGET_PI_ZERO_2 is defined.
 *
 * Pi Zero 2 UART pins: GPIO14 (TXD), GPIO15 (RXD) - typically /dev/ttyS0 or /dev/ttyAMA0
 * For USB-serial adapter: /dev/ttyUSB0
 */
class UartBridge {
public:
    using MessageCallback = std::function<void(const std::string& topic, const std::string& payload)>;

    UartBridge();
    ~UartBridge();

    UartBridge(const UartBridge&) = delete;
    UartBridge& operator=(const UartBridge&) = delete;

    /**
     * Open UART port.
     * @param device e.g. /dev/ttyS0, /dev/ttyAMA0, /dev/ttyUSB0
     * @param baud_rate e.g. 115200
     * @return true on success
     */
    bool open(const std::string& device, int baud_rate = 115200);
    void close();

    bool isOpen() const { return fd_ >= 0; }

    void setMessageCallback(MessageCallback cb) { msg_callback_ = std::move(cb); }

    /**
     * Send message to ESP32. Format: "topic|payload\n"
     */
    bool send(const std::string& topic, const std::string& payload);

    /**
     * Read available data and invoke callback for complete messages.
     * Call from main loop. Returns false on fatal error.
     */
    bool poll();

private:
    int fd_ = -1;
    std::string rx_buffer_;
    MessageCallback msg_callback_;
    static constexpr size_t RX_BUF_SIZE = 256;
};

} // namespace desk
