"""Manage LM75 sensor."""

import asyncio
from adafruit_pct2075 import PCT2075
from typing import Callable, Union
from boneio.const import STATE, SENSOR, LM75

from boneio.helper.exceptions import I2CError


class LM75Sensor:
    """Represent LM75 sensor in BoneIO."""

    def __init__(
        self,
        i2c,
        address,
        topic_prefix: str,
        name: str,
        send_message: Callable[[str, Union[str, dict]], None],
        id: str = LM75,
    ):
        """Initialize LM75 class."""
        self._id = id
        self._name = name
        self._send_message = send_message
        self._send_topic = f"{topic_prefix}/{SENSOR}/{self._id}"
        try:
            self._pct = PCT2075(i2c_bus=i2c, address=address)
        except ValueError as err:
            raise I2CError(err)

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def state(self):
        """Give rounded value of temperature."""
        return round(self._pct.temperature, 2)

    async def send_state(self):
        """Fetch temperature periodically and send to MQTT."""
        while True:
            self._send_message(
                topic=self._send_topic,
                payload={STATE: self.state},
            )
            await asyncio.sleep(60)
