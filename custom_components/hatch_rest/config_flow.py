"""Config flow for Hatch Rest integration."""
from __future__ import annotations

import logging
from typing import Any

from pyhatchbabyrest import connect_async
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_connection(hass: HomeAssistant, mac_address: str, device_name: str | None = None) -> dict[str, Any]:
    """Validate we can connect to the device.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        # Attempt to connect to the device
        rest = await connect_async(mac_address)

        # Get initial state to confirm connection works
        await rest.refresh_data()

        # Disconnect
        await rest.disconnect()

        # Use device name if provided, otherwise use MAC address
        title = device_name if device_name else f"Hatch Rest ({mac_address[-8:]})"

        # Return info that you want to store in the config entry
        return {
            "title": title,
            "unique_id": mac_address.replace(":", "").lower(),
        }

    except Exception as err:
        _LOGGER.exception("Failed to connect to Hatch Rest at %s", mac_address)
        raise CannotConnect from err


class HatchRestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hatch Rest."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address.replace(":", "").lower())
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        assert self._discovery_info is not None

        if user_input is not None:
            try:
                info = await validate_connection(
                    self.hass, self._discovery_info.address, self._discovery_info.name
                )
            except CannotConnect:
                return self.async_abort(reason="cannot_connect")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error")
                return self.async_abort(reason="unknown")

            return self.async_create_entry(
                title=info["title"],
                data={CONF_ADDRESS: self._discovery_info.address},
            )

        self._set_confirm_only()

        placeholders = {
            "name": self._discovery_info.name or "Hatch Rest",
            "address": self._discovery_info.address,
        }

        self.context["title_placeholders"] = placeholders

        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=placeholders,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            mac_address = user_input[CONF_ADDRESS].upper()

            # Check if already configured
            await self.async_set_unique_id(mac_address.replace(":", "").lower())
            self._abort_if_unique_id_configured()

            try:
                info = await validate_connection(self.hass, mac_address)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data={CONF_ADDRESS: mac_address},
                )

        # Show form with discovered devices or manual entry
        # Get all discovered Hatch devices
        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass):
            # Check for Hatch Rest (original) or Hatch Rest+ by manufacturer data
            is_hatch = False
            if discovery_info.manufacturer_data:
                # Manufacturer ID 1076 (0x0434) is Hatch Baby
                if 1076 in discovery_info.manufacturer_data:
                    is_hatch = True
            # Also check for original Hatch Rest service UUID
            if discovery_info.service_uuids and "02260001-5efd-47eb-9c1a-de53f7a2b232" in discovery_info.service_uuids:
                is_hatch = True
            
            if (
                discovery_info.address.replace(":", "").lower() not in current_addresses
                and is_hatch
            ):
                self._discovered_devices[
                    discovery_info.address
                ] = discovery_info

        if self._discovered_devices:
            # Show selection of discovered devices
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_ADDRESS): vol.In(
                            {
                                address: f"{info.name or 'Hatch Rest'} ({address})"
                                for address, info in self._discovered_devices.items()
                            }
                        ),
                    }
                ),
                errors=errors,
            )

        # No discovered devices, show manual entry
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): str,
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
