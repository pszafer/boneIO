"""GPIO Relay module."""

import asyncio
from typing import Callable, Union
from .const import STATE, RELAY
from .gpio import setup_output, read_input, write_output, HIGH, LOW
import logging

_LOGGER = logging.getLogger(__name__)


class GpioRelay:
    """Represents GPIO Relay output"""

    def __init__(
        self,
        pin: str,
        send_message: Callable[[str, Union[str, dict]], None],
        topic_prefix: str,
        id: str = None,
    ) -> None:
        """Initialize Gpio relay."""
        self._pin = pin
        self._id = id
        setup_output(self._pin)
        write_output(self.pin, LOW)
        self._send_message = send_message
        self._relay_topic = f"{topic_prefix}/{RELAY}/"
        self._loop = asyncio.get_running_loop()
        _LOGGER.debug("Setup relay with pin %s", self._pin)

    @property
    def id(self) -> bool:
        return self._id or self._pin

    @property
    def is_active(self) -> bool:
        """Is relay active."""
        return read_input(self.pin, on_state=HIGH)

    @property
    def pin(self) -> str:
        """PIN of the relay"""
        return self._pin

    def turn_on(self) -> None:
        """Call turn on action."""
        write_output(self.pin, HIGH)
        self._loop.call_soon_threadsafe(self.send_state)

    def turn_off(self) -> None:
        """Call turn off action."""
        write_output(self.pin, LOW)
        self._loop.call_soon_threadsafe(self.send_state)

    def toggle(self) -> None:
        """Toggle relay."""
        if self.is_active:
            self.turn_off()
        else:
            self.turn_on()

    def send_state(self) -> None:
        """Send state to Mqtt on action."""
        self._send_message(
            topic=f"{self._relay_topic}{self._pin}", payload={STATE: self.is_active}
        )
