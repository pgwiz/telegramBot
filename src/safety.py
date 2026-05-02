"""Resilience helpers: retry/backoff, circuit-breaker-lite, error decorator."""
from __future__ import annotations

import asyncio
import functools
import logging
import random
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def async_retry(
    *,
    attempts: int = 5,
    base: float = 1.5,
    max_delay: float = 30.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Exponential backoff with jitter for async functions."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc: BaseException | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:  # type: ignore[misc]
                    last_exc = exc
                    if attempt >= attempts:
                        break
                    delay = min(max_delay, (base ** attempt)) + random.uniform(0, 0.5)
                    logger.warning(
                        "%s failed (attempt %d/%d): %s — retrying in %.1fs",
                        func.__name__, attempt, attempts, exc, delay,
                    )
                    await asyncio.sleep(delay)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


def safe_handler(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """Wrap a Telegram handler so a single bad message never kills the bot."""

    @functools.wraps(func)
    async def wrapper(update, context, *args: Any, **kwargs: Any):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception:
            logger.exception("Handler %s blew up", func.__name__)
            try:
                if update and getattr(update, "effective_message", None):
                    await update.effective_message.reply_text(
                        "Yikes — something tripped on my end. Try again in a sec."
                    )
            except Exception:
                pass

    return wrapper
