"""Sensor module."""
from boneio.sensor.lm75 import LM75Sensor
from boneio.sensor.gpio import GpioInputSensor

__all__ = ["LM75Sensor", "GpioInputSensor"]
