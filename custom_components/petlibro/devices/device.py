"""Module containing the Device class for interacting with PetLibro devices."""

from logging import getLogger
from typing import cast

from homeassistant.helpers.device_registry import format_mac

from ..api import PetLibroAPI
from .event import EVENT_UPDATE, Event

_LOGGER = getLogger(__name__)


class Device(Event):
    """Class representing a PetLibro device."""

    def __init__(self, data: dict, api: PetLibroAPI) -> None:
        """Initialize the Device with data and API.

        :param data: Dictionary containing device data.
        :param api: Instance of PetLibroAPI for interacting with the device.
        """
        super().__init__()
        self._data: dict = {}
        self.api = api
        _LOGGER.debug("Creating device: %s", data)

        self.update_data(data)

    def update_data(self, data: dict) -> None:
        """Save the device info from a data dictionary."""
        self._data.update(data)
        self.emit(EVENT_UPDATE)

    async def refresh(self):
        """Refresh the device data from the API."""
        data = {}
        data.update(await self.api.device_base_info(self.serial))
        data.update(await self.api.device_real_info(self.serial))
        self.update_data(data)

    @property
    def serial(self) -> str:
        """Return the serial number of the device."""
        return cast(str, self._data.get("deviceSn"))

    @property
    def model(self) -> str:
        """Return the model identifier of the device."""
        return cast(str, self._data.get("productIdentifier"))

    @property
    def model_name(self) -> str:
        """Return the model name of the device."""
        return cast(str, self._data.get("productName"))

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return cast(str, self._data.get("name"))

    @property
    def mac(self) -> str:
        """Return the MAC address of the device."""
        return cast(str, format_mac(self._data.get("mac")))

    @property
    def software_version(self) -> str:
        """Return the software version of the device."""
        return cast(str, self._data.get("softwareVersion"))

    @property
    def hardware_version(self) -> str:
        """Return the hardware version of the device."""
        return cast(str, self._data.get("hardwareVersion"))
