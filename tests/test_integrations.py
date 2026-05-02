"""Integrations are auto-discovered and have the expected shape."""
from __future__ import annotations

import pytest

import integrations


def test_load_all_registers_known_plugins():
    integrations.load_all()
    names = set(integrations.all_integrations().keys())
    expected = {"weather", "price", "joke", "fetch", "scrape"}
    missing = expected - names
    assert not missing, f"Missing integrations: {missing}"


def test_each_integration_has_metadata():
    integrations.load_all()
    for name, plug in integrations.all_integrations().items():
        assert plug.name == name
        assert plug.description
        assert plug.usage


@pytest.mark.asyncio
async def test_jokes_offline_fallback(monkeypatch):
    integrations.load_all()
    plug = integrations.get("joke")
    assert plug is not None

    import httpx

    class _BoomClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, *args, **kwargs):
            raise httpx.ConnectError("no network in tests")

    monkeypatch.setattr("integrations.jokes.httpx.AsyncClient", _BoomClient)
    res = await plug.run()
    assert res.ok
    assert isinstance(res.text, str) and res.text


@pytest.mark.asyncio
async def test_fetch_requires_url():
    integrations.load_all()
    plug = integrations.get("fetch")
    res = await plug.run()
    assert not res.ok
    assert "Usage" in res.text
