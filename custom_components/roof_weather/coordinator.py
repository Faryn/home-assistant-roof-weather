"""Polling and HTML parsing for the roof weather station."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
import re
from zoneinfo import ZoneInfo

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, NAME, STATION_URL, UPDATE_INTERVAL

BERLIN_TZ = ZoneInfo("Europe/Berlin")
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class RoofWeatherReading:
    """Normalized current values published by the station."""

    measured_at: datetime
    temperature: float | None
    humidity: float | None
    rain_intensity: float | None
    rain_today: float | None
    wind_speed: float | None
    wind_gust: float | None
    wind_direction: float | None
    pressure: float | None


class RoofWeatherCoordinator(DataUpdateCoordinator[RoofWeatherReading]):
    """Fetch and normalize current station readings."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            logger=LOGGER,
            name=NAME,
            update_interval=UPDATE_INTERVAL,
            always_update=False,
        )

    async def _async_update_data(self) -> RoofWeatherReading:
        """Fetch the public page and parse the current readings."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(STATION_URL, timeout=15) as response:
                response.raise_for_status()
                return parse_roof_station_html(await response.text())
        except Exception as err:  # Home Assistant presents this as unavailable.
            raise UpdateFailed(f"Error fetching roof weather station: {err}") from err


def parse_roof_station_html(html: str) -> RoofWeatherReading:
    """Parse the stable labels from the station's mobile HTML page."""
    text = _html_to_text(html)
    timestamp = _first_match(text, r"Messung vom:\s*(\d{2}\.\d{2}\.\d{2})\s*-\s*(\d{2}:\d{2}:\d{2})")
    if timestamp is None:
        raise ValueError("Station measurement timestamp was not found")
    date_part, time_part = timestamp
    measured_at = datetime.strptime(f"{date_part} {time_part}", "%d.%m.%y %H:%M:%S").replace(tzinfo=BERLIN_TZ)
    return RoofWeatherReading(
        measured_at=measured_at,
        temperature=_hero_temperature(html) or _number_after_label(text, "Aktuell"),
        humidity=_number_after_label(text, "Rel. Luftfeuchte"),
        rain_intensity=_number_after_label(text, "Intensität"),
        rain_today=_number_after_label(text, "Tages-Summe"),
        wind_speed=_number_after_label(text, "Windgeschwindigkeit"),
        wind_gust=_number_after_label(text, "Böen"),
        wind_direction=_number_after_label(text, "Windrichtung"),
        pressure=_number_after_label(text, "Luftdruck relativ"),
    )


def _html_to_text(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", "\n", html)
    text = text.replace("&nbsp;", " ").replace("&deg;", "°")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def _first_match(text: str, pattern: str) -> tuple[str, str] | None:
    match = re.search(pattern, text, flags=re.I | re.S)
    return match.groups() if match else None


def _number_after_label(text: str, label: str) -> float | None:
    match = re.search(rf"{re.escape(label)}\s*\n\s*(-?\d[\d\.]*,\d+|-?\d+(?:\.\d+)?)", text, flags=re.I)
    return _german_number(match.group(1)) if match else None


def _german_number(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def _hero_temperature(html: str) -> float | None:
    match = re.search(r'class="hero-temp".*?class="big">\s*(-?\d[\d\.]*,\d+|-?\d+(?:\.\d+)?)\s*</div>.*?Temperatur', html, flags=re.I | re.S)
    return _german_number(match.group(1)) if match else None
