"""Sanity checks for the offline personality engine."""
from __future__ import annotations

import pytest

import personality


def test_basic_pools_non_empty():
    assert personality.joke()
    assert personality.roast()
    assert personality.fun_fact()
    assert personality.comeback()


@pytest.mark.parametrize("vibe", ["funny", "pro", "chill"])
def test_stylize_vibes(vibe: str):
    out = personality.stylize("hello", vibe)
    assert isinstance(out, str)
    assert "hello" in out


def test_stylize_unknown_vibe_falls_back_to_funny():
    out = personality.stylize("hi", "weirdvibe")
    assert "hi" in out


@pytest.mark.asyncio
async def test_reply_to_falls_back_when_no_llm(monkeypatch):
    # No LLM_API_KEY → should return canned response.
    out = await personality.reply_to("anything", vibe="funny")
    assert isinstance(out, str)
    assert len(out) > 0
