from .ioinput import GpioInputButton
from .iorelay import GpioRelay
from .const import (
    ACTION,
    ACTIONS,
    GPIO,
    ID,
    KIND,
    OUTPUT,
    PIN,
    SINGLE,
    RELAY,
    ON,
    OFF,
    ONLINE,
    STATE,
    ClickTypes,
)
from typing import Callable, Optional, Union, List
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)


def ha_availibilty_message(topic, relay_id):
    """Create availability topic for HA."""
    return {
        "availability": [{"topic": f"{topic}/{STATE}"}],
        "command_topic": f"{topic}/relay/{relay_id}/set",
        "device": {
            "identifiers": [topic],
            "manufacturer": "BoneIO",
            "model": "BoneIO Relay Board",
            "name": f"BoneIO {topic}",
            "sw_version": "0.0.1",
        },
        "name": f"Relay {relay_id}",
        "payload_off": OFF,
        "payload_on": ON,
        "state_topic": f"{topic}/{RELAY}/{relay_id}",
        "unique_id": f"{topic}{RELAY}{relay_id}",
        "value_template": "{{ value_json.state }}",
    }


class Manager:
    """Manager to communicate MQTT with GPIO inputs and outputs."""

    def __init__(
        self,
        send_message: Callable[[str, Union[str, dict]], None],
        topic_prefix: str,
        relay_pins: List,
        input_pins: List,
        ha_discovery: bool = True,
        ha_discovery_prefix: str = "homeassistant",
        relay_input_map: Optional[List] = None,
    ) -> None:
        """Initialize the manager."""
        self.send_message = send_message
        self._topic_prefix = topic_prefix
        self.relay_topic = f"{topic_prefix}/{RELAY}/+/set"
        self._input_pins = input_pins
        loop = asyncio.get_event_loop()

        def choose_output(pin_kind=GPIO):
            if pin_kind == GPIO:
                return GpioRelay

        self.output = {
            gpio[ID]: choose_output(gpio[KIND])(
                pin=gpio[PIN],
                id=gpio[ID],
                send_message=self.send_message,
                topic_prefix=topic_prefix,
            )
            for gpio in relay_pins
        }
        self._relay_input_map = relay_input_map
        for out in self.output.values():
            if ha_discovery:
                _LOGGER.debug("Sending HA discovery.")
                self.send_ha_autodiscovery(relay=out.id, prefix=ha_discovery_prefix)
            loop.call_soon_threadsafe(
                loop.call_later,
                0.5,
                out.send_state,
            )

        self.buttons = [
            GpioInputButton(
                pin=gpio[PIN],
                press_callback=lambda x, i: self.press_callback(x, i, gpio[ACTIONS]),
                rest_pin=gpio,
            )
            for gpio in self._input_pins
        ]

        self.send_message(topic=f"{topic_prefix}/{STATE}", payload=ONLINE)
        _LOGGER.info("Manager ready to handle input and outputs.")

    def press_callback(self, x: ClickTypes, inpin: str, actions: dict) -> None:
        """Press callback to use in input gpio.
        If relay input map is provided also toggle action on relay."""
        self.send_message(topic=f"{self._topic_prefix}/input/{inpin}", payload=x)
        action = actions.get(x)
        if action:
            if action[ACTION] == OUTPUT:
                """For now only output type is supported"""
                output_gpio = self.output.get(action[PIN])
                if output_gpio:
                    output_gpio.toggle()

    def send_ha_autodiscovery(self, relay: str, prefix: str) -> None:
        """Send HA autodiscovery information for each relay."""
        msg = ha_availibilty_message(self._topic_prefix, relay_id=relay)
        topic = f"{prefix}/switch/{self._topic_prefix}/switch/config"
        self.send_message(topic=topic, payload=msg)

    def receive_message(self, topic: str, message: str) -> None:
        """Callback for receiving action from Mqtt."""
        extracted_relay = topic.replace(f"{self._topic_prefix}/{RELAY}/", "").replace(
            "/set", ""
        )
        target_device = self.output.get(extracted_relay)
        if target_device:
            if message == ON:
                target_device.turn_on()
            elif message == OFF:
                target_device.turn_off()
