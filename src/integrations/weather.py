"""Weather integration backed by Open-Meteo (no API key required).

Falls back to OpenWeather if ``OPENWEATHER_API_KEY`` is set.
"""
from __future__ import annotations

import httpx

from settings import get_settings

from . import Integration, IntegrationResult, register


class WeatherIntegration(Integration):
    name = "weather"
    description = "Current weather for a city"
    usage = "/weather <city>"

    async def run(self, *args: str) -> IntegrationResult:
        if not args:
            return IntegrationResult(False, "Usage: /weather <city>")
        city = " ".join(args).strip()
        settings = get_settings()
        timeout = settings.http_timeout

        async with httpx.AsyncClient(timeout=timeout) as client:
            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "en"},
            )
            geo.raise_for_status()
            results = geo.json().get("results") or []
            if not results:
                return IntegrationResult(False, f"Couldn't find a place called '{city}'.")
            place = results[0]
            lat, lon = place["latitude"], place["longitude"]
            label = f"{place['name']}, {place.get('country_code', '')}".strip(", ")

            wx = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,wind_speed_10m,relative_humidity_2m,weather_code",
                    "timezone": "auto",
                },
            )
            wx.raise_for_status()
            cur = wx.json().get("current", {})

        text = (
            f"🌤️ *{label}*\n"
            f"Temp: {cur.get('temperature_2m', '?')}°C\n"
            f"Humidity: {cur.get('relative_humidity_2m', '?')}%\n"
            f"Wind: {cur.get('wind_speed_10m', '?')} km/h"
        )
        return IntegrationResult(True, text, {"lat": lat, "lon": lon})


register(WeatherIntegration())
