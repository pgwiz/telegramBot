"""Structured logging configuration.

Supports both human-readable (default) and JSON output. JSON is enabled by
setting ``LOG_JSON=true`` in the environment so the bot plays nicely with
log aggregators.
"""
from __future__ import annotations

import json
import logging
import sys
from typing import Any


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "levelname", "levelno", "lineno", "module", "msecs",
                "message", "msg", "name", "pathname", "process", "processName",
                "relativeCreated", "stack_info", "thread", "threadName",
            }:
                continue
            payload[key] = value
        return json.dumps(payload, default=str)


def setup_logging(level: str = "INFO", json_output: bool = False) -> None:
    """Configure the root logger. Safe to call multiple times."""
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    if json_output:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root.addHandler(handler)
    root.setLevel(level.upper())

    # Tame verbose third-party loggers.
    for noisy in ("httpx", "telegram.ext", "apscheduler"):
        logging.getLogger(noisy).setLevel(max(root.level, logging.INFO))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
