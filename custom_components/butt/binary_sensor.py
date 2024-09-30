from __future__ import annotations

import logging

from dataclasses import dataclass
from datetime import datetime
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    EntityCategory,
    BinarySensorDeviceClass,
)

from typing import Optional

from homeassistant.const import CONF_NAME
from homeassistant.core import callback
import homeassistant.util.dt as dt_util

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
)

from .hub import ButtHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for sensor_description in SENSOR_TYPES.values():
        sensor = ButtBinarySensor(
            hub_name,
            hub,
            device_info,
            sensor_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True


class ButtBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Ampere Storage Pro Modbus sensor."""

    def __init__(
        self,
        platform_name: str,
        hub: ButtHub,
        device_info,
        description: ButtBinarySensorEntityDescription,
    ):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self.entity_description: ButtBinarySensorEntityDescription = description

        super().__init__(coordinator=hub)

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self.entity_description.key}"

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return (
            self.coordinator.data[self.entity_description.key]
            if self.entity_description.key in self.coordinator.data
            else None
        )


@dataclass
class ButtBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes Zoonneplan sensor entities."""


SENSOR_TYPES: dict[str, list[ButtBinarySensorEntityDescription]] = {
    "Connected": ButtBinarySensorEntityDescription(
        name="Connected",
        key="connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=True,
    ),
    "Connecting": ButtBinarySensorEntityDescription(
        name="Connecting",
        key="connecting",
        entity_registry_enabled_default=True,
    ),
    "SignalDetected": ButtBinarySensorEntityDescription(
        name="Signal Detected",
        key="signaldetected",
        entity_registry_enabled_default=True,
    ),
    "SilenceDetected": ButtBinarySensorEntityDescription(
        name="Silence Detected",
        key="silencedetected",
        entity_registry_enabled_default=True,
    ),
    "Recording": ButtBinarySensorEntityDescription(
        name="Recording",
        key="recording",
        icon="mdi:record-rec",
        entity_registry_enabled_default=True,
    ),
    "ExtendedPacket": ButtBinarySensorEntityDescription(
        name="Extended Packet",
        key="extendedpacket",
        entity_registry_enabled_default=True,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}
