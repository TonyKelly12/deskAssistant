#include "uart_bridge.hpp"
#include "uart_protocol.hpp"
#include <iostream>
#include <cstring>

#if defined(__linux__) || defined(__unix__)
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <errno.h>
#endif

namespace desk {

#if defined(__linux__) || defined(__unix__)

UartBridge::UartBridge() = default;

UartBridge::~UartBridge() {
    close();
}

bool UartBridge::open(const std::string& device, int baud_rate) {
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }

    fd_ = ::open(device.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd_ < 0) {
        std::cerr << "UART open failed: " << device << " - " << strerror(errno) << std::endl;
        return false;
    }

    struct termios tty;
    if (tcgetattr(fd_, &tty) != 0) {
        std::cerr << "UART tcgetattr failed: " << strerror(errno) << std::endl;
        ::close(fd_);
        fd_ = -1;
        return false;
    }

    speed_t speed = B115200;
    switch (baud_rate) {
        case 9600:   speed = B9600;   break;
        case 19200:  speed = B19200;  break;
        case 38400:  speed = B38400;  break;
        case 57600:  speed = B57600;  break;
        case 115200: speed = B115200; break;
        case 230400: speed = B230400; break;
        case 460800: speed = B460800; break;
        case 921600: speed = B921600; break;
        default: break;
    }

    cfsetispeed(&tty, speed);
    cfsetospeed(&tty, speed);

    tty.c_cflag &= ~PARENB;
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CSIZE;
    tty.c_cflag |= CS8;
    tty.c_cflag &= ~CRTSCTS;
    tty.c_cflag |= CREAD | CLOCAL;

    tty.c_lflag &= ~ICANON;
    tty.c_lflag &= ~ECHO;
    tty.c_lflag &= ~ECHOE;
    tty.c_lflag &= ~ECHONL;
    tty.c_lflag &= ~ISIG;

    tty.c_iflag &= ~(IXON | IXOFF | IXANY);
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);

    tty.c_oflag &= ~OPOST;
    tty.c_oflag &= ~ONLCR;

    tty.c_cc[VTIME] = 1;
    tty.c_cc[VMIN] = 0;

    if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
        std::cerr << "UART tcsetattr failed: " << strerror(errno) << std::endl;
        ::close(fd_);
        fd_ = -1;
        return false;
    }

    rx_buffer_.clear();
    std::cout << "UART opened: " << device << " @" << baud_rate << std::endl;
    return true;
}

void UartBridge::close() {
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }
}

bool UartBridge::send(const std::string& topic, const std::string& payload) {
    if (fd_ < 0) return false;

    std::string line = uart_protocol::encode(topic, payload);
    ssize_t n = ::write(fd_, line.data(), line.size());
    if (n != static_cast<ssize_t>(line.size())) {
        std::cerr << "UART write failed: " << strerror(errno) << std::endl;
        return false;
    }
    return true;
}

bool UartBridge::poll() {
    if (fd_ < 0) return true;

    char buf[RX_BUF_SIZE];
    ssize_t n = ::read(fd_, buf, sizeof(buf));
    if (n > 0) {
        rx_buffer_.append(buf, static_cast<size_t>(n));
        size_t pos;
        while ((pos = rx_buffer_.find('\n')) != std::string::npos) {
            std::string line = rx_buffer_.substr(0, pos);
            rx_buffer_.erase(0, pos + 1);

            std::string topic, payload;
            if (uart_protocol::decode(line, topic, payload) && msg_callback_) {
                msg_callback_(topic, payload);
            }
        }
        if (rx_buffer_.size() > 4096) rx_buffer_.clear();
    } else if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
        std::cerr << "UART read error: " << strerror(errno) << std::endl;
        return false;
    }
    return true;
}

#else

UartBridge::UartBridge() = default;

UartBridge::~UartBridge() = default;

bool UartBridge::open(const std::string&, int) {
    return false;
}

void UartBridge::close() {}

bool UartBridge::send(const std::string&, const std::string&) {
    return false;
}

bool UartBridge::poll() {
    return true;
}

#endif

} // namespace desk
