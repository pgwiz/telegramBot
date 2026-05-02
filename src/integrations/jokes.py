"""Online dad-joke integration. Falls back to local jokes if the API is down."""
from __future__ import annotations

import httpx

import personality
from settings import get_settings

from . import Integration, IntegrationResult, register


class JokesIntegration(Integration):
    name = "joke"
    description = "Fetch a fresh joke (online, with offline fallback)"
    usage = "/joke"

    async def run(self, *args: str) -> IntegrationResult:
        settings = get_settings()
        try:
            async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
                r = await client.get(
                    "https://icanhazdadjoke.com/",
                    headers={"Accept": "application/json", "User-Agent": "telegramBot/1.0"},
                )
                r.raise_for_status()
                return IntegrationResult(True, r.json().get("joke", personality.joke()))
        except Exception:
            return IntegrationResult(True, personality.joke())


register(JokesIntegration())
