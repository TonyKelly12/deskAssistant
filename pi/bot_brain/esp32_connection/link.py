"""Serial link to ESP32 (topic|payload\\n style — match esp32/uart_mqtt_bridge.ino)."""

from __future__ import annotations

import threading
from typing import Callable, Optional


class Esp32Link:
    def __init__(
        self,
        device: str = "/dev/serial0",
        baud: int = 115200,
        on_line: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self.device = device
        self.baud = baud
        self._on_line = on_line
        self._ser = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def connect(self) -> bool:
        """Open serial port. Requires pyserial: pip install pyserial"""
        try:
            import serial
        except ImportError:
            return False
        try:
            self._ser = serial.Serial(self.device, self.baud, timeout=0.1)
            return True
        except OSError:
            return False

    def send(self, topic: str, payload: str) -> None:
        if self._ser is None:
            return
        line = f"{topic}|{payload}\n".encode()
        self._ser.write(line)

    def close(self) -> None:
        self._running = False
        if self._ser is not None:
            self._ser.close()
            self._ser = None
