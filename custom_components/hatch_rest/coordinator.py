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
    """Class to manage fetching Hatch Rest data from the device.

    Hatch Rest 1st gen only supports a single BLE connection at a time.
    The underlying pyhatchbabyrest library already connects and disconnects
    per operation (via BleakClient context managers), so we do NOT hold a
    persistent connection. We keep a client reference only for the cached
    BLEDevice scan result. The poll interval is intentionally long (5 min)
    to minimize contention with the Hatch phone app.
    """

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

    def _read_client_state(self) -> dict[str, Any]:
        """Read current state from the client's cached properties."""
        return {
            "is_on": self.client.power,
            "brightness": self.client.brightness,
            "color": self.client.color,
            "volume": self.client.volume,
            "sound": self.client.sound.value if hasattr(self.client.sound, 'value') else 0,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        await self._ensure_client()

        try:
            await self.client.refresh_data()
            return self._read_client_state()

        except Exception as err:
            _LOGGER.warning("Error fetching Hatch Rest data: %s", err)
            self.client = None
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def _ensure_client(self) -> None:
        """Ensure we have a client with a cached BLEDevice reference.

        This does NOT hold a persistent BLE connection — it just scans for
        the device once so subsequent operations know the BLE address.
        """
        async with self._connect_lock:
            if self.client and self.client.device:
                return

            _LOGGER.debug("Scanning for Hatch Rest at %s", self.mac_address)

            try:
                self.client = await connect_async(self.mac_address)
                _LOGGER.info("Successfully found Hatch Rest")

            except Exception as err:
                _LOGGER.error("Failed to find Hatch Rest: %s", err)
                raise UpdateFailed(f"Failed to connect: {err}") from err

    async def _execute_command(self, func, description: str) -> None:
        """Run a command and push the resulting state to listeners.

        The library already reads state after each command internally,
        so we use async_set_updated_data to push it immediately instead
        of scheduling another poll (which would open yet another BLE
        connection).
        """
        await self._ensure_client()

        try:
            await func()
            self.async_set_updated_data(self._read_client_state())
        except Exception as err:
            _LOGGER.error("Failed to %s: %s", description, err)
            raise

    async def set_power(self, is_on: bool) -> None:
        """Turn device on or off."""
        async def _do():
            if is_on:
                await self.client.power_on()
            else:
                await self.client.power_off()
        await self._execute_command(_do, "set power")

    async def set_color(self, red: int, green: int, blue: int) -> None:
        """Set the RGB color."""
        async def _do():
            await self.client.set_color(red, green, blue)
        await self._execute_command(_do, "set color")

    async def set_brightness(self, brightness: int) -> None:
        """Set brightness (0-100)."""
        async def _do():
            await self.client.set_brightness(brightness)
        await self._execute_command(_do, "set brightness")

    async def set_volume(self, volume: int) -> None:
        """Set volume (0-100)."""
        async def _do():
            await self.client.set_volume(volume)
        await self._execute_command(_do, "set volume")

    async def set_sound(self, sound: int) -> None:
        """Set the sound/audio track."""
        async def _do():
            await self.client.set_sound(sound)
        await self._execute_command(_do, "set sound")

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        self.client = None
