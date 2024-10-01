from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

import logging
from typing import Callable, Optional

from homeassistant.const import CONF_NAME
from homeassistant.core import callback
import homeassistant.util.dt as dt_util

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
)

from .hub import ButtHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    hub_name = config_entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for button_description in BUTTON_TYPES.values():
        button = ButtButton(
            hub_name,
            hub,
            device_info,
            button_description,
        )
        entities.append(button)

    async_add_entities(entities)


class ButtButton(CoordinatorEntity, ButtonEntity):
    """Representation of an Ampere Storage Pro Modbus sensor."""

    def __init__(
        self,
        platform_name: str,
        hub: ButtHub,
        device_info,
        description: ButtButtonEntityDescription,
    ):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self.entity_description: ButtButtonEntityDescription = description
        self.hub = hub

        super().__init__(coordinator=hub)

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self.entity_description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""

        # if self.entity_description.key == "startrecord":
        #    await self.hub.start_record()  # Ruft die Funktion aus hub.py auf
        # elif self.entity_description.key == "stoprecord":
        #    await self.hub.stop_record()  # Ruft die Stop-Funktion auf
        if self.entity_description.buttonFunction:
            await self.entity_description.buttonFunction(self.hub)
        else:
            _LOGGER.error("No function defined for this button")


@dataclass
class ButtButtonEntityDescription(ButtonEntityDescription):
    """A class that describes Zoonneplan sensor entities."""

    buttonFunction: Optional[Callable] = field(default=None)


BUTTON_TYPES: dict[str, list[ButtButtonEntityDescription]] = {
    "Connect": ButtButtonEntityDescription(
        name="Connect",
        key="connect",
        buttonFunction=lambda hub: hub.connect(),
    ),
    "Disconnect": ButtButtonEntityDescription(
        name="Disconnect",
        key="disconnect",
        buttonFunction=lambda hub: hub.disconnect(),
    ),
    "StartRecord": ButtButtonEntityDescription(
        name="Start Record",
        key="startrecord",
        buttonFunction=lambda hub: hub.start_record(),
    ),
    "StopRecord": ButtButtonEntityDescription(
        name="Stop Record",
        key="stoprecord",
        buttonFunction=lambda hub: hub.stop_record(),
    ),
}
