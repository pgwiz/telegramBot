"""Retry decorator smoke test."""
from __future__ import annotations

import pytest

from safety import async_retry


@pytest.mark.asyncio
async def test_async_retry_succeeds_after_failures():
    counter = {"n": 0}

    @async_retry(attempts=3, base=1.0, max_delay=0.0)
    async def flaky():
        counter["n"] += 1
        if counter["n"] < 2:
            raise ValueError("nope")
        return "ok"

    assert await flaky() == "ok"
    assert counter["n"] == 2


@pytest.mark.asyncio
async def test_async_retry_gives_up():
    @async_retry(attempts=2, base=1.0, max_delay=0.0)
    async def always_fails():
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError):
        await always_fails()
