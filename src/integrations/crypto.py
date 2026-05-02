"""Crypto price integration backed by CoinGecko (no API key required)."""
from __future__ import annotations

import httpx

from settings import get_settings

from . import Integration, IntegrationResult, register

_ALIAS = {
    "btc": "bitcoin", "eth": "ethereum", "sol": "solana", "ada": "cardano",
    "doge": "dogecoin", "xrp": "ripple", "ltc": "litecoin", "bnb": "binancecoin",
    "avax": "avalanche-2", "matic": "matic-network",
}


class CryptoIntegration(Integration):
    name = "price"
    description = "Live crypto price (USD)"
    usage = "/price <symbol|coingecko-id>"

    async def run(self, *args: str) -> IntegrationResult:
        if not args:
            return IntegrationResult(False, "Usage: /price <symbol> e.g. /price btc")
        symbol = args[0].lower()
        coin_id = _ALIAS.get(symbol, symbol)

        settings = get_settings()
        async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
            r = await client.get(
                f"{settings.coingecko_base.rstrip('/')}/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                },
            )
            r.raise_for_status()
            data = r.json().get(coin_id)
        if not data:
            return IntegrationResult(False, f"Couldn't find '{symbol}'. Try the full id, e.g. ethereum.")
        price = data.get("usd")
        change = data.get("usd_24h_change", 0.0) or 0.0
        arrow = "🟢" if change >= 0 else "🔴"
        text = f"{arrow} *{coin_id.upper()}* — ${price:,.4f} ({change:+.2f}% / 24h)"
        return IntegrationResult(True, text, {"coin_id": coin_id, "usd": price})


register(CryptoIntegration())
