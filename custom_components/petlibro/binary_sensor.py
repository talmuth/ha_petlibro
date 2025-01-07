"""Support for PETLIBRO sensors."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from logging import getLogger

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PetLibroHubConfigEntry
from .devices import Device
from .devices.fountains.dockstream_smart_fountain import DockstreamSmartFountain
from .entity import PetLibroEntity, PetLibroEntityDescription, _DeviceT

_LOGGER = getLogger(__name__)


@dataclass(frozen=True)
class PetLibroBinarySensorEntityDescription(
    BinarySensorEntityDescription, PetLibroEntityDescription[_DeviceT]
):
    """A class that describes device sensor entities."""


class PetLibroBinarySensorEntity(PetLibroEntity[_DeviceT], BinarySensorEntity):
    """PETLIBRO sensor entity."""

    entity_description: PetLibroBinarySensorEntityDescription[_DeviceT]

    @cached_property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return bool(getattr(self.device, self.entity_description.key))


DEVICE_BINARY_SENSOR_MAP: dict[
    type[Device], list[PetLibroBinarySensorEntityDescription]
] = {
    DockstreamSmartFountain: [
        PetLibroBinarySensorEntityDescription[DockstreamSmartFountain](
            key="filter_replacement_required",
            translation_key="filter_replacement_required",
            icon="mdi:filter-remove",
            device_class=BinarySensorDeviceClass.PROBLEM,
        ),
        PetLibroBinarySensorEntityDescription[DockstreamSmartFountain](
            key="cleaning_required",
            translation_key="cleaning_required",
            icon="mdi:spray-bottle",
            device_class=BinarySensorDeviceClass.PROBLEM,
        ),
    ],
}


async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO binary sensors using config entry."""
    hub = entry.runtime_data
    entities = [
        PetLibroBinarySensorEntity(device, hub, description)
        for device in hub.devices
        for device_type, entity_descriptions in DEVICE_BINARY_SENSOR_MAP.items()
        if isinstance(device, device_type)
        for description in entity_descriptions
    ]
    async_add_entities(entities)
