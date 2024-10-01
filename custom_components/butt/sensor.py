from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    EntityCategory,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.const import UnitOfTime, UnitOfInformation
import logging
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
        sensor = ButtSensor(
            hub_name,
            hub,
            device_info,
            sensor_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True


class ButtSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Butt sensor."""

    def __init__(
        self,
        platform_name: str,
        hub: ButtHub,
        device_info,
        description: ButtSensorEntityDescription,
    ):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self.entity_description: ButtSensorEntityDescription = description

        super().__init__(coordinator=hub)

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self.entity_description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            self.coordinator.data[self.entity_description.key]
            if self.entity_description.key in self.coordinator.data
            else None
        )


@dataclass
class ButtSensorEntityDescription(SensorEntityDescription):
    """A class that describes Zoonneplan sensor entities."""


SENSOR_TYPES: dict[str, list[ButtSensorEntityDescription]] = {
    "StreamSeconds": ButtSensorEntityDescription(
        name="Stream Seconds",
        key="streamseconds",
        icon="mdi:timer-music",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_registry_enabled_default=True,
    ),
    "StreamKBytes": ButtSensorEntityDescription(
        name="Stream kBytes",
        key="streamkbytes",
        icon="mdi:speedometer",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.KILOBYTES,
        # state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    "RecordSeconds": ButtSensorEntityDescription(
        name="Record Seconds",
        key="recordseconds",
        icon="mdi:timer-music",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_registry_enabled_default=True,
    ),
    "RecordKBytes": ButtSensorEntityDescription(
        name="Record kBytes",
        key="recordkbytes",
        icon="mdi:speedometer",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.KILOBYTES,
        # state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    "VolumeLeft": ButtSensorEntityDescription(
        name="Volume Left",
        key="volumeleft",
        icon="mdi:volume-high",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    "VolumeRight": ButtSensorEntityDescription(
        name="Volume Right",
        key="volumeright",
        icon="mdi:volume-high",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    "Song": ButtSensorEntityDescription(
        name="Song",
        key="song",
        icon="mdi:music",
        entity_registry_enabled_default=True,
    ),
    "RecordPath": ButtSensorEntityDescription(
        name="Record Path",
        key="recordpath",
        icon="mdi:file-music",
        entity_registry_enabled_default=True,
    ),
    "Listeners": ButtSensorEntityDescription(
        name="Listeners",
        key="listeners",
        icon="mdi:account-voice",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "Version": ButtSensorEntityDescription(
        name="Version",
        key="version",
        icon="mdi:information-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "IpAdress": ButtSensorEntityDescription(
        name="IP Adress",
        key="ipadress",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "Port": ButtSensorEntityDescription(
        name="port",
        key="port",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}
