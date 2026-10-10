# Roof Weather Station for Home Assistant

Custom Home Assistant integration for a local rooftop weather station.

It polls the public station page every five minutes and exposes current
temperature, humidity, rain, wind, pressure, and the station's measurement
time as native Home Assistant sensors.

## Install

Copy `custom_components/roof_weather` into Home Assistant's `/config/custom_components/`,
restart Home Assistant, then add **Roof weather station** from **Settings →
Devices & services → Add integration**.

The station page is public and needs no credentials.
