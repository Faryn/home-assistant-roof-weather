"""Constants for the roof weather station integration."""

from datetime import timedelta

DOMAIN = "roof_weather"
NAME = "Roof weather station"
STATION_URL = "https://www.arrowdynamics.systems/wetterdaten_mobile.php"
UPDATE_INTERVAL = timedelta(minutes=5)
MANUFACTURER = "Arrow Dynamics"
MODEL = "Rooftop weather station"
