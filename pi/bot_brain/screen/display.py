"""GC9A01 / SPI screen — hook your real driver here (see repo scripts/spi_display_scaffold.py)."""

from __future__ import annotations


class Screen:
    def __init__(self) -> None:
        self._ready = False

    def setup(self) -> None:
        """Open SPI / init controller."""
        self._ready = True

    @property
    def ready(self) -> bool:
        return self._ready
