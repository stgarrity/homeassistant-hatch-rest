"""Data update coordinator for Hatch Rest integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from pyhatchbabyrest import PyHatchBabyRestAsync, connect_async

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class HatchRestDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Hatch Rest data from the device."""

    def __init__(
        self,
        hass: HomeAssistant,
        mac_address: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.mac_address = mac_address
        self.client: PyHatchBabyRestAsync | None = None
        self._connect_lock = asyncio.Lock()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        # Ensure we're connected
        if not self.client or not self.client.connected:
            await self._ensure_connected()

        try:
            # Refresh device state
            await self.client.refresh_data()

            return {
                "is_on": self.client.is_on,
                "brightness": self.client.brightness,
                "color": self.client.color,
                "volume": self.client.volume,
                "sound": getattr(self.client, "current_sound", 0),
            }

        except Exception as err:
            # Connection might be lost, try to reconnect on next update
            _LOGGER.warning("Error fetching Hatch Rest data: %s", err)
            if self.client:
                try:
                    await self.client.disconnect()
                except Exception:  # pylint: disable=broad-except
                    pass
                self.client = None
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def _ensure_connected(self) -> None:
        """Ensure we are connected to the device."""
        async with self._connect_lock:
            if self.client and self.client.connected:
                return

            _LOGGER.debug("Connecting to Hatch Rest at %s", self.mac_address)

            try:
                self.client = await connect_async(mac_address=self.mac_address)
                _LOGGER.info("Successfully connected to Hatch Rest")

            except Exception as err:
                _LOGGER.error("Failed to connect to Hatch Rest: %s", err)
                raise UpdateFailed(f"Failed to connect: {err}") from err

    async def set_power(self, is_on: bool) -> None:
        """Turn device on or off."""
        await self._ensure_connected()

        try:
            if is_on:
                await self.client.power_on()
            else:
                await self.client.power_off()

            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Failed to set power: %s", err)
            raise

    async def set_color(self, red: int, green: int, blue: int) -> None:
        """Set the RGB color."""
        await self._ensure_connected()

        try:
            await self.client.set_color(red, green, blue)
            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Failed to set color: %s", err)
            raise

    async def set_brightness(self, brightness: int) -> None:
        """Set brightness (0-100)."""
        await self._ensure_connected()

        try:
            await self.client.set_brightness(brightness)
            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Failed to set brightness: %s", err)
            raise

    async def set_volume(self, volume: int) -> None:
        """Set volume (0-100)."""
        await self._ensure_connected()

        try:
            await self.client.set_volume(volume)
            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Failed to set volume: %s", err)
            raise

    async def set_sound(self, sound: int) -> None:
        """Set the sound/audio track."""
        await self._ensure_connected()

        try:
            await self.client.set_sound(sound)
            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Failed to set sound: %s", err)
            raise

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and disconnect."""
        if self.client and self.client.connected:
            _LOGGER.debug("Disconnecting from Hatch Rest")
            try:
                await self.client.disconnect()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Error disconnecting: %s", err)
            finally:
                self.client = None
