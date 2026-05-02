"""APScheduler wiring: starts a background loop and registers default jobs.

Adding a custom job is a one-liner — see ``register_job`` in
:mod:`autonomy.jobs` for the pattern. Jobs are crash-isolated; one failing
job won't kill the scheduler.
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="UTC")
    return _scheduler


def add_cron(name: str, cron: str, func: Callable[..., Awaitable[None]], **kwargs) -> None:
    """Schedule an async coroutine to run on a cron expression (UTC)."""
    sched = get_scheduler()
    trigger = CronTrigger.from_crontab(cron, timezone="UTC")
    sched.add_job(
        func, trigger=trigger, name=name, kwargs=kwargs,
        coalesce=True, max_instances=1, misfire_grace_time=300,
    )
    logger.info("Scheduled cron job '%s' (%s)", name, cron)


def add_interval(name: str, seconds: int, func: Callable[..., Awaitable[None]], **kwargs) -> None:
    sched = get_scheduler()
    sched.add_job(
        func, trigger=IntervalTrigger(seconds=seconds), name=name, kwargs=kwargs,
        coalesce=True, max_instances=1, misfire_grace_time=60,
    )
    logger.info("Scheduled interval job '%s' (every %ds)", name, seconds)


def start() -> None:
    sched = get_scheduler()
    if not sched.running:
        sched.start()
        logger.info("Scheduler started")


def shutdown() -> None:
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
