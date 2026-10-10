"""Sensor entities for the roof weather station."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import DEGREE, PERCENTAGE, UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, NAME
from .coordinator import RoofWeatherCoordinator, RoofWeatherReading


@dataclass(frozen=True, kw_only=True)
class RoofWeatherSensorDescription(SensorEntityDescription):
    """Describe one station metric."""

    value_fn: Callable[[RoofWeatherReading], float | None]


SENSORS: tuple[RoofWeatherSensorDescription, ...] = (
    RoofWeatherSensorDescription(key="temperature", name="Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.temperature),
    RoofWeatherSensorDescription(key="humidity", name="Humidity", native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.HUMIDITY, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.humidity),
    RoofWeatherSensorDescription(key="rain_intensity", name="Rain intensity", native_unit_of_measurement="mm/h", device_class=SensorDeviceClass.PRECIPITATION_INTENSITY, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.rain_intensity),
    RoofWeatherSensorDescription(key="rain_today", name="Rain today", native_unit_of_measurement="mm", device_class=SensorDeviceClass.PRECIPITATION, state_class=SensorStateClass.TOTAL, value_fn=lambda data: data.rain_today),
    RoofWeatherSensorDescription(key="wind_speed", name="Wind speed", native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR, device_class=SensorDeviceClass.WIND_SPEED, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.wind_speed),
    RoofWeatherSensorDescription(key="wind_gust", name="Wind gust", native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR, device_class=SensorDeviceClass.WIND_SPEED, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.wind_gust),
    RoofWeatherSensorDescription(key="wind_direction", name="Wind direction", native_unit_of_measurement=DEGREE, device_class=SensorDeviceClass.WIND_DIRECTION, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.wind_direction),
    RoofWeatherSensorDescription(key="pressure", name="Relative pressure", native_unit_of_measurement=UnitOfPressure.HPA, device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.pressure),
)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up roof weather sensors."""
    coordinator: RoofWeatherCoordinator = entry.runtime_data
    async_add_entities(RoofWeatherSensor(coordinator, description) for description in SENSORS)


class RoofWeatherSensor(CoordinatorEntity[RoofWeatherCoordinator], SensorEntity):
    """One current metric from the roof station."""

    entity_description: RoofWeatherSensorDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: RoofWeatherCoordinator, description: RoofWeatherSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "local_roof_station")},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=NAME,
        )

    @property
    def native_value(self) -> float | None:
        """Return the latest value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Keep the station's own measurement time visible on each sensor."""
        return {"measured_at": self.coordinator.data.measured_at.isoformat()}
