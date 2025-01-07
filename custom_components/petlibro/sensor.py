"""Support for PETLIBRO sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from logging import getLogger
from typing import Any, cast

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfMass, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PetLibroHubConfigEntry
from .devices import Device
from .devices.feeders.feeder import Feeder
from .devices.feeders.granary_feeder import GranaryFeeder
from .devices.fountains.dockstream_smart_fountain import DockstreamSmartFountain
from .entity import PetLibroEntity, PetLibroEntityDescription, _DeviceT

_LOGGER = getLogger(__name__)


def icon_for_gauge_level(gauge_level: int | None = None, offset: int = 0) -> str:
    """Return a gauge icon valid identifier."""
    if gauge_level is None or gauge_level <= 0 + offset:
        return "mdi:gauge-empty"
    if gauge_level > 70 + offset:
        return "mdi:gauge-full"
    if gauge_level > 30 + offset:
        return "mdi:gauge"
    return "mdi:gauge-low"


def unit_of_measurement_feeder(device: Feeder) -> str | None:
    """Return the unit of measurement for the feeder."""
    return device.unit_type


def device_class_feeder(device: Feeder) -> SensorDeviceClass | None:
    """Return the device class for the feeder."""
    if device.unit_type in [UnitOfMass.OUNCES, UnitOfMass.GRAMS]:
        return SensorDeviceClass.WEIGHT
    if device.unit_type in ["cup", UnitOfVolume.MILLILITERS]:
        return SensorDeviceClass.VOLUME
    return None


@dataclass(frozen=True)
class PetLibroSensorEntityDescription(
    SensorEntityDescription, PetLibroEntityDescription[_DeviceT]
):
    """A class that describes device sensor entities."""

    icon_fn: Callable[[Any], str | None] = lambda _: None
    native_unit_of_measurement_fn: Callable[[_DeviceT], str | None] = lambda _: None
    device_class_fn: Callable[[_DeviceT], SensorDeviceClass | None] = lambda _: None
    should_report: Callable[[_DeviceT], bool] = lambda _: True


class PetLibroSensorEntity(PetLibroEntity[_DeviceT], SensorEntity):  # type: ignore [reportIncompatibleVariableOverride]
    """PETLIBRO sensor entity."""

    entity_description: PetLibroSensorEntityDescription[_DeviceT]  # type: ignore [reportIncompatibleVariableOverride]

    @cached_property
    def native_value(self) -> float | datetime | str | None:
        """Return the state."""
        if self.entity_description.should_report(self.device):
            if isinstance(
                val := getattr(self.device, self.entity_description.key), str
            ):
                return val.lower()
            return cast(float | datetime | None, val)
        return None

    @cached_property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if (icon := self.entity_description.icon_fn(self.state)) is not None:
            return icon
        return super().icon

    @cached_property
    def native_unit_of_measurement(self) -> str | None:
        """Return the native unit of measurement to use in the frontend, if any."""
        if (
            native_unit_of_measurement
            := self.entity_description.native_unit_of_measurement_fn(self.device)
        ) is not None:
            return native_unit_of_measurement
        return super().native_unit_of_measurement

    @cached_property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class to use in the frontend, if any."""
        if (
            device_class := self.entity_description.device_class_fn(self.device)
        ) is not None:
            return device_class
        return super().device_class


DEVICE_SENSOR_MAP: dict[type[Device], list[PetLibroSensorEntityDescription]] = {
    GranaryFeeder: [
        PetLibroSensorEntityDescription[GranaryFeeder](
            key="remaining_desiccant",
            translation_key="remaining_desiccant",
            icon="mdi:package",
        ),
        PetLibroSensorEntityDescription[GranaryFeeder](
            key="today_feeding_quantity",
            translation_key="today_feeding_quantity",
            icon="mdi:scale",
            native_unit_of_measurement_fn=unit_of_measurement_feeder,
            device_class_fn=device_class_feeder,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        PetLibroSensorEntityDescription[GranaryFeeder](
            key="today_feeding_times",
            translation_key="today_feeding_times",
            icon="mdi:history",
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
    ],
    DockstreamSmartFountain: [
        PetLibroSensorEntityDescription[DockstreamSmartFountain](
            key="water_level",
            translation_key="water_level",
            icon="mdi:water-percent",
            state_class=SensorStateClass.TOTAL,
            native_unit_of_measurement=PERCENTAGE,
        ),
        PetLibroSensorEntityDescription[DockstreamSmartFountain](
            key="remaining_water",
            translation_key="remaining_water",
            icon="mdi:water",
            state_class=SensorStateClass.TOTAL,
            device_class=SensorDeviceClass.VOLUME,
            native_unit_of_measurement=UnitOfVolume.MILLILITERS,
        ),
        PetLibroSensorEntityDescription[DockstreamSmartFountain](
            key="today_water_consumption",
            translation_key="today_water_consumption",
            icon="mdi:fountain",
            state_class=SensorStateClass.TOTAL_INCREASING,
            device_class=SensorDeviceClass.VOLUME,
            native_unit_of_measurement=UnitOfVolume.MILLILITERS,
        ),
        PetLibroSensorEntityDescription[DockstreamSmartFountain](
            key="days_before_filter_replacement",
            translation_key="days_before_filter_replacement",
            icon="mdi:counter",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.DAYS,
        ),
        PetLibroSensorEntityDescription[DockstreamSmartFountain](
            key="days_before_cleaning",
            translation_key="days_before_cleaning",
            icon="mdi:counter",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.DAYS,
        ),
    ],
}


async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO sensors using config entry."""
    hub = entry.runtime_data
    entities = [
        PetLibroSensorEntity(device, hub, description)
        for device in hub.devices
        for device_type, entity_descriptions in DEVICE_SENSOR_MAP.items()
        if isinstance(device, device_type)
        for description in entity_descriptions
    ]
    async_add_entities(entities)
