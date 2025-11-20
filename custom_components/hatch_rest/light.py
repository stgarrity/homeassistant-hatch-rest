"""Light platform for Hatch Rest integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import HatchRestDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hatch Rest light from a config entry."""
    coordinator: HatchRestDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([HatchRestLight(coordinator, entry)])


class HatchRestLight(CoordinatorEntity[HatchRestDataUpdateCoordinator], LightEntity):
    """Representation of a Hatch Rest light."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    def __init__(
        self,
        coordinator: HatchRestDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)

        # Unique ID
        self._attr_unique_id = f"{entry.entry_id}_light"

        # Device info - use the entry title as the device name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            connections={(CONNECTION_BLUETOOTH, coordinator.mac_address)},
        )

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator.data.get("is_on", False)

    @property
    def brightness(self) -> int:
        """Return the brightness of the light (0-255)."""
        # Convert from 0-100 to 0-255
        brightness_pct = self.coordinator.data.get("brightness", 0)
        return int(brightness_pct * 2.55)

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the RGB color value."""
        return self.coordinator.data.get("color", (255, 255, 255))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        # Handle color change
        if ATTR_RGB_COLOR in kwargs:
            red, green, blue = kwargs[ATTR_RGB_COLOR]
            await self.coordinator.set_color(red, green, blue)

        # Handle brightness change
        if ATTR_BRIGHTNESS in kwargs:
            # Convert from 0-255 to 0-100
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            await self.coordinator.set_brightness(brightness)

        # If just turning on without specific color/brightness, use power_on
        if ATTR_RGB_COLOR not in kwargs and ATTR_BRIGHTNESS not in kwargs:
            await self.coordinator.set_power(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.coordinator.set_power(False)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
